#!/usr/bin/env python

from typing import Optional
import pandas as pd
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, listen, start, router, or_

from reconciliationflow.crews.anomaly_detection.anomaly_detection import AnomalyDetection
from reconciliationflow.crews.anomaly_review.anomaly_review import AnomalyReview

keyColumns = ["Company", "Account", "AU", "Currency"]
criteriaColumns = ["GL Balance", "IHub Balance"]
derivedColumns = ["Balance Difference"],
historicalColumns = ["Account", "Secondary Account", "Primary Account"]
dateColumns = ["As of Date"]


class ReconciliationState(BaseModel):
    metadata: str = ""
    historicalData: str = ""
    realtimeData: str = ""
    report: str = ""
    valid: bool = False
    feedback: Optional[str] = None
    retryCount: int = 0


class ReconciliatonFlow(Flow[ReconciliationState]):
    """Flow for analysis & classification"""

    @start()
    def generate_input(self):
        #Generate the reconciliation input
        historical_df = pd.read_excel("IHub Reconciliation.xlsx", sheet_name="Historical")
        self.state.historicalData = historical_df.astype(str).to_json(orient = 'records')

        realtime_df = pd.read_excel("IHub Reconciliation.xlsx", sheet_name="Real Time")
        self.state.realtimeData = realtime_df.astype(str).to_json(orient = 'records')

        self.state.metadata = f"keyColumns: {keyColumns}, criteriaColumns: {criteriaColumns}, derivedColumns: {derivedColumns}, historicalColumns: {historicalColumns}, dateColumns: {dateColumns}"

        return self.state


    @listen(or_(generate_input, "retry"))
    def generate_analysis(self, state):
        print("Analysing the data provided & generating analysis report")
        result = (
            AnomalyDetection().crew().kickoff(inputs={
                "metadata": state.metadata,
                "historicalData": state.historicalData,
                "realtimeData": state.realtimeData,
                "feedback": state.feedback
            })
        )

        #Store the content
        self.state.report = result.raw

    @router(generate_analysis)
    def evaluate_analysis(self):
        if self.state.retryCount > 3:
            return "max_try_exceeded"

        result = AnomalyReview().crew().kickoff(inputs={
            "report": self.state.report
        })

        self.state.valid = result["valid"]
        self.state.feedback = result["feedback"]
        self.state.retryCount += 1

        if self.state.valid:
            return "completed"

        print("RETRY")
        return "retry"

    @listen("completed")
    def save_result(self):
        pass

    @listen("max_try_exceeded")
    def max_retry_exceeded_exit(self):
        pass



def kickoff():
    ReconciliatonFlow().kickoff()


if __name__ == "__main__":
    kickoff()
