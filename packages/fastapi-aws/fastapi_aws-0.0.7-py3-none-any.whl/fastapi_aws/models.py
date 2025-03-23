"""Pydantic models for the AWS API integration validation
"""
class IntegrationType(str, Enum):
    AWS_PROXY = "aws_proxy"
    AWS = "aws"
    MOCK = "mock"


class Integration(BaseModel):
    """Baseclass for defining integrations
    TODO: build the integrations with classes and then export to dict.
    """

    type: IntegrationType
    requestTemplates: Dict[str, Any]
    responses: Dict[str, Any]

    def model_dump(self) -> Dict[str, Any]:
        return {"x-amazon-apigateway-integration": super().model_dump()}


class LambdaJSONRequestTemplate(BaseModel):
    body: str
    httpMethod: str = "POST"
    resource: str = "/"
    path: str = "/"
    pathParameters: Optional[Dict[str, str]] = None


class MockIntegration(Integration):
    type: IntegrationType = IntegrationType.MOCK


class ServiceIntegration(Integration):
    uri: str = Field(..., description="arn of the called resource")
    credentials: str = Field(..., description="arn of the IAM used to invoke the resource")
    httpMethod: str = "POST"


class LambdaIntegration(ServiceIntegration):
    type: IntegrationType = IntegrationType.AWS_PROXY
    # uri must be lambda arn


class StepFunctionIntegration(ServiceIntegration):
    type: IntegrationType = IntegrationType.AWS
    # uri: "arn:aws:apigateway:${region}:states:action/StartSyncExecution"


class NotImplementedIntegration(MockIntegration):
    requestTemplates: Dict[str, Any] = {"application/json": {"statusCode": 200}}
    responses: Dict[str, Any] = {
        "default": {
            "statusCode": "200",
            "responseTemplates": {"application/json": '{"status": "not implemented"}'},
        }
    }
