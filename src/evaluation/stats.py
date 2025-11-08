import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import bootstrap
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
import statsmodels.api as sm

from evaluation.exam import ExamTaker
from evaluation.simulation import TutoringType
from utils.logger_config import logger


class StatisticsCalculator:
    def __init__(self):
        self.answer_preds_df = self._prep_answer_preds_df()
        self.learner_scores_df = self._get_learner_scores(self.answer_preds_df)

    def calculate_eval_stats(self) -> None:
        """
        Main function to get all statistics from SAILED experiments.
        Calculates and displays evaluation statistics for exam results.

        - Builds and prints summary tables of learner accuracy by
            level and tutoring type
        - Generates and saves plots for average scores and number of turns
            by prior knowledge level
        - Performs statistical tests (regression and ANOVA) on the number
            of turns.

        Side Effects:
            - Prints summary tables to stdout.
            - Saves plots to the 'figures' directory.
            - Prints regression and ANOVA results to stdout.

        Returns:
            None
        """
        table_a = self.build_table_A()
        print(table_a)

        table_b = self.build_table_B()
        print(table_b)

        self.plot_and_export_avg_score_by_prior_status()
        self.plot_export_and_test_avg_turns_by_prior_status()

    def build_table_A(
        self, n_boot: int = 10000, ci: float = 0.95
    ) -> pd.DataFrame:
        """
        Builds a summary table of learner score by
        overall knowledge level and tutoring type.

        This method calculates the mean accuracy and bootstrap
        confidence intervals for each learner level (beginner,
        intermediate, advanced, overall) and each tutoring type.
        The results are returned as a pandas DataFrame.

        Args:
            n_boot (int, optional): Number of bootstrap samples for
                confidence intervals. Defaults to 10,000.
            ci (float, optional): Confidence interval level. Defaults to 0.95.

        Returns:
            pd.DataFrame: A DataFrame containing learner level, tutoring type,
                mean accuracy, confidence interval bounds, and number
                of learners.
        """
        rows = []
        for level in ["beginner", "intermediate", "advanced"]:
            for tutoring_type in [t.value for t in TutoringType]:
                vals = self.learner_scores_df[
                    (self.learner_scores_df.learner_level == level)
                    & (self.learner_scores_df.tutoring_type == tutoring_type)
                ]["score"].values
                mean, lo, hi = self._mean_ci_with_bootstrap(
                    vals,  # type: ignore
                    n_boot=n_boot,
                    ci=ci,
                )
                rows.append(
                    {
                        "learner_level": level,
                        "tutoring_type": tutoring_type,
                        "mean_accuracy": mean,
                        "ci_low": lo,
                        "ci_high": hi,
                        "n_learners": int(len(vals)),
                    }
                )

        # overall rows
        for tutoring_type in [t.value for t in TutoringType]:
            vals = self.learner_scores_df[
                self.learner_scores_df.tutoring_type == tutoring_type
            ]["score"].values
            mean, lo, hi = self._mean_ci_with_bootstrap(
                vals,  # type: ignore
                n_boot=n_boot,
                ci=ci,
            )
            rows.append(
                {
                    "learner_level": "overall",
                    "tutoring_type": tutoring_type,
                    "mean_accuracy": mean,
                    "ci_low": lo,
                    "ci_high": hi,
                    "n_learners": int(len(vals)),
                }
            )

        table_A = pd.DataFrame(rows)
        table_A["cond_order"] = table_A["tutoring_type"].map(
            {c: i for i, c in enumerate([t.value for t in TutoringType])}
        )
        table_A = (
            table_A.sort_values(["learner_level", "cond_order"])
            .drop(columns=["cond_order"])
            .reset_index(drop=True)
        )
        return table_A

    def build_table_B(
        self, n_boot: int = 10000, ci: float = 0.95
    ) -> pd.DataFrame:
        """
        Builds a summary table of score differences between tutoring types,
        by learner level.

        This method calculates the mean difference and bootstrap confidence
        intervals for learner scores between pairs of tutoring types
        (vanilla vs. no_tutoring, atlas vs. vanilla) for each learner level
        (beginner, intermediate, advanced, overall). The results are returned
        as a pandas DataFrame.

        Args:
            n_boot (int, optional): Number of bootstrap samples for confidence
                intervals. Defaults to 10,000.
            ci (float, optional): Confidence interval level. Defaults to 0.95.

        Returns:
            pd.DataFrame: A DataFrame containing learner level,
                comparison, mean difference, confidence interval bounds,
                and number of learners.
        """

        def diffs_block(g: pd.DataFrame, level_label: str) -> pd.DataFrame:
            pvt = g.pivot_table(
                index="learner_id",
                columns="tutoring_type",
                values="score",
                aggfunc="mean",
            )
            rows = []
            for a, b in [
                ("vanilla", "no_tutoring"),
                ("atlas", "vanilla"),
            ]:
                if a not in pvt.columns or b not in pvt.columns:
                    continue
                diffs = (pvt[a] - pvt[b]).dropna().values
                mean, lo, hi = self._mean_ci_with_bootstrap(
                    diffs,  # type: ignore
                    n_boot=n_boot,
                    ci=ci,
                )
                rows.append(
                    {
                        "learner_level": level_label,
                        "comparison": f"{a} - {b}",
                        "mean_diff": mean,
                        "ci_low": lo,
                        "ci_high": hi,
                        "n_learners": int(len(diffs)),
                    }
                )
            return pd.DataFrame(rows)

        parts = []
        for learner_level in ["beginner", "intermediate", "advanced"]:
            parts.append(
                diffs_block(
                    self.learner_scores_df[
                        self.learner_scores_df.learner_level == learner_level
                    ],
                    learner_level,
                )
            )
        parts.append(diffs_block(self.learner_scores_df, "overall"))

        table_B = pd.concat(parts, ignore_index=True)
        table_B = table_B.sort_values(
            ["learner_level", "comparison"]
        ).reset_index(drop=True)
        return table_B

    def plot_and_export_avg_score_by_prior_status(self) -> None:
        """
        Generates and saves a bar plot of average exam scores by
        prior knowledge status in concepts, and tutoring type.

        This method groups exam results by tutoring type and
        concept status prior to enrollment, calculates the mean score
        for each group, and creates a bar plot using seaborn.
        The plot is saved as a PNG file in the 'figures' directory.

        Side Effects:
            - Saves the plot to 'figures/avg_score_by_prior_status.png'.

        Returns:
            None
        """
        avg_scores = (
            self.answer_preds_df.groupby(
                ["prior_level", "tutoring_type"], as_index=False
            )["correct"]
            .mean()
            .rename(columns={"correct": "mean_score"})
        )  # type: ignore

        cond_order = ["no_tutoring", "vanilla", "atlas"]
        avg_scores["tutoring_type"] = pd.Categorical(
            avg_scores["tutoring_type"], categories=cond_order, ordered=True
        )

        plt.figure(figsize=(8, 5))
        ax = sns.barplot(
            data=avg_scores,
            x="prior_level",
            y="mean_score",
            hue="tutoring_type",
            palette="Set2",
            edgecolor="black",
        )

        ax.set_ylim(0, 1)
        ax.set_xlabel("Prior KC status")
        ax.set_ylabel("Average exam scores")
        ax.set_title(
            "Average exam scores by prior KC status and tutoring type"
        )
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])

        # Add value labels to each bar
        for container in ax.containers:
            ax.bar_label(
                container,  # type: ignore
                fmt="%.2f",
                label_type="edge",
                padding=2,
            )

        dirpath = Path(__file__).resolve().parent / "figures"
        dirpath.mkdir(exist_ok=True)
        out_path = dirpath / "avg_score_by_prior_status.png"
        ax.legend(title="Tutoring Type", frameon=False)
        plt.tight_layout()
        plt.savefig(out_path, dpi=200)
        plt.close()
        logger.info(f"Saved plot: {out_path}")

    def plot_export_and_test_avg_turns_by_prior_status(self) -> None:
        """
        Generates and saves a boxplot of the number of chat turns
        by learner knowledge status per concept, prior to enrollment.

        This method groups ATLAS chat sessions by concept and prior
        knowledge status, calculates the number of turns for each concept,
        and creates a boxplot using seaborn. The plot is saved as a PNG
        file in the 'figures' directory. It also performs OLS regression
        and ANOVA to test for differences in the number of turns across
        prior knowledge statuses, printing the results to stdout.

        Side Effects:
            - Saves the plot to 'figures/avg_turns_by_prior_status.png'.
            - Prints regression and ANOVA results to stdout.

        Returns:
            None
        """
        confused_turns = []
        not_started_turns = []
        mastered_turns = []

        for i in range(1, 10):
            learner_id = f"learner_{i}"
            df_learner = self.answer_preds_df[
                self.answer_preds_df["learner_id"] == learner_id
            ]

            concept_chats = ExamTaker.group_messages_by_concept(
                learner_id=learner_id, tutoring_type=TutoringType.ATLAS
            )

            for concept_chat in concept_chats:
                concept_id = concept_chat.concept_id
                prior_level = df_learner[
                    df_learner["concept_id"] == concept_id
                ]["prior_level"].values
                prior_level = prior_level[0]
                n_turns = len(concept_chat.messages) // 2

                if prior_level == "confused":
                    confused_turns.append(n_turns)
                elif prior_level == "not_started":
                    not_started_turns.append(n_turns)
                elif prior_level == "mastered":
                    mastered_turns.append(n_turns)

        # Prepare data for seaborn boxplot
        data = (
            [("confused", t) for t in confused_turns]
            + [("not_started", t) for t in not_started_turns]
            + [("mastered", t) for t in mastered_turns]
        )
        plot_df = pd.DataFrame(data, columns=["prior_level", "n_turns"])

        plt.figure(figsize=(8, 5))
        ax = sns.boxplot(
            data=plot_df,
            y="prior_level",
            x="n_turns",
            order=["confused", "not_started", "mastered"],
            palette="Set2",
        )
        ax.set_ylabel("Prior KC status")
        ax.set_xlabel("Number of turns")
        ax.set_title("Distribution of turns by prior KC status")

        dirpath = Path(__file__).resolve().parent / "figures"
        dirpath.mkdir(exist_ok=True)
        out_path = dirpath / "avg_turns_by_prior_status.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=200)
        plt.close()
        logger.info(f"Saved boxplot: {out_path}")

        # ensure prior_level is categorical with "mastered" first
        plot_df["prior_level"] = pd.Categorical(
            plot_df["prior_level"],
            categories=[
                "mastered",
                "not_started",
                "confused",
            ],  # mastered = baseline
            ordered=False,
        )

        # OLS regression with mastered as reference
        model = smf.ols(
            "n_turns ~ C(prior_level, Treatment(reference='mastered'))",
            data=plot_df,
        ).fit()

        print(model.summary())

        # ANOVA table: overall test
        anova_table = sm.stats.anova_lm(model, typ=2)
        print("\nANOVA table:\n", anova_table)

    def _mean_ci_with_bootstrap(
        self,
        vals: np.ndarray,
        n_boot: int = 10000,
        ci: float = 0.95,
        seed: int = 42,
    ) -> tuple[float, float, float]:
        """
        Calculates the mean and bootstrap confidence interval
        for an array of values.

        This method computes the mean of the input values and uses bootstrap
        resampling to estimate the lower and upper bounds of the confidence
        interval.

        Args:
            vals (np.ndarray): Array of values to analyze.
            n_boot (int, optional): Number of bootstrap samples.
                Defaults to 10,000.
            ci (float, optional): Confidence interval level. Defaults to 0.95.
            seed (int, optional): Random seed for reproducibility.
                Defaults to 42.

        Returns:
            tuple[float, float, float]: The mean, lower bound, and upper bound
                of the confidence interval.
        """
        mean = vals.mean()
        rng = np.random.default_rng(seed)
        res = bootstrap(
            (vals,),
            np.mean,
            vectorized=False,
            n_resamples=n_boot,
            confidence_level=ci,
            method="percentile",
            rng=rng,
        )
        lo = float(res.confidence_interval.low)
        hi = float(res.confidence_interval.high)
        return mean, lo, hi

    def _get_learner_scores(
        self, exam_results_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Computes mean exam accuracy for each learner and tutoring type.

        This method groups the exam results by learner ID and tutoring type,
        calculates the mean score (accuracy) for each group, and merges the
        learner level information. The result is a DataFrame with one row per
        (learner_id, tutoring_type), including the learner's level.

        Args:
            exam_results_df (pd.DataFrame): DataFrame containing exam results
                with columns for learner_id, tutoring_type, and correctness.

        Returns:
            pd.DataFrame: DataFrame with columns for learner_id, tutoring_type,
                mean score, and learner level.
        """
        learner_scores = exam_results_df.groupby(
            ["learner_id", "tutoring_type"], as_index=False
        )["correct"].mean()
        learner_scores = learner_scores.rename(columns={"correct": "score"})  # type: ignore
        levels = exam_results_df[
            ["learner_id", "learner_level"]
        ].drop_duplicates()
        learner_scores = learner_scores.merge(
            levels, on="learner_id", how="left"
        )
        return learner_scores

    def _prep_answer_preds_df(self) -> pd.DataFrame:
        """
        Loads and prepares the exam results DataFrame for analysis.

        This method reads all CSV files in the 'exam_results' directory,
        concatenates them, and adds columns for correctness (whether the
        answer is 'A', as it is always the correct answer), learner level
        (inferred from learner ID), and prior knowledge level
        (as a categorical variable).

        Returns:
            pd.DataFrame: A DataFrame containing all exam results, with
                additional columns for correctness, learner level, and
                prior knowledge level.
        """

        def infer_level_from_learner_id(learner_id: str) -> str:
            """Map learner_1 to 9 -> beginner/intermediate/advanced."""
            m = re.search(r"(\d+)$", learner_id)
            if not m:
                raise ValueError(f"Invalid learner_id format: {learner_id}")
            n = int(m.group(1))
            if 1 <= n <= 3:
                return "beginner"
            if 4 <= n <= 6:
                return "intermediate"
            if 7 <= n <= 9:
                return "advanced"
            return "unknown"

        exam_results_dir = Path(__file__).resolve().parent / "exam_results"

        # read all csv files (one per learner)
        dfs = []
        for csv_file in exam_results_dir.glob("*.csv"):
            df = pd.read_csv(csv_file)
            dfs.append(df)

        # transform choice to correct (checking if A was the choice)
        answer_preds_df = pd.concat(dfs, ignore_index=True)
        answer_preds_df["correct"] = (answer_preds_df["choice"] == "A").astype(
            int
        )
        # map learner overall knowledge category
        answer_preds_df["learner_level"] = answer_preds_df["learner_id"].map(
            infer_level_from_learner_id
        )
        answer_preds_df["prior_level"] = pd.Categorical(
            answer_preds_df["prior_level"],
            categories=["confused", "not_started", "mastered"],
            ordered=True,
        )
        return answer_preds_df
