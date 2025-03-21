from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
import boto3
from io import StringIO
import pandas as pd

def data_explainer_report(df):
    """
    Generates a data explainer report for a Pandas DataFrame.
    Args:
        df (pd.DataFrame): The DataFrame to analyze.
    Returns:
        dict: A dictionary containing the data quality report.
    """
    report = {}
    report["describe_stats"] = df.describe().to_dict()
    report["missing_values"] = df.isnull().sum().to_dict()
    report["duplicates"] = df.duplicated().sum()
    report["counts"] = {
        "rows": len(df),
        "columns": len(df.columns)
    }
    report["basics"] = {
        "columns": list(df.columns)
    }
    return report


class DataQualityInput(BaseModel):
    """Input for data quality check operations."""
    bucket: str = Field(
        description="S3 bucket in which the data is stored"
    )
    file_path: str = Field(
        description="Path of the file in the bucket"
    )


class DataQualityTool(BaseTool):
    """Tool for checking data quality of files in S3."""
    
    name: str = "check_data_quality"
    description: str = "Use this for data quality check on files stored in S3"
    args_schema: type[BaseModel] = DataQualityInput
    return_direct: bool = False
    
    def _run(self, bucket: str, file_path: str, **kwargs):
        try:
            s3_client = boto3.client('s3')
            csv_obj = s3_client.get_object(Bucket=bucket, Key=file_path)
            df = pd.read_csv(StringIO(csv_obj['Body'].read().decode('utf-8')))

            report = data_explainer_report(df)

            response = []
            response.append(f"Data Quality Report for {file_path}:")
            response.append(f"- Total rows: {report['counts']['rows']}")
            response.append(f"- Total columns: {report['counts']['columns']}")
            response.append(f"- Number of duplicates: {report['duplicates']}")

            # Report missing values if any exist
            missing = {k: v for k, v in report['missing_values'].items() if v > 0}
            if missing:
                response.append("\nMissing values found in columns:")
                for col, count in missing.items():
                    response.append(f"- {col}: {count} missing values")

            return "\n".join(response)

        except Exception as e:
            return f"Error checking data quality: {str(e)}"
    
    async def _arun(
        self,
        bucket: str,
        file_path: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        return self._run(bucket=bucket, file_path=file_path)
