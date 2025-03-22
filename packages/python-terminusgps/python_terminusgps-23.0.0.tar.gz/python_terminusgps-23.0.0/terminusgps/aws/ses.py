import boto3
import json


class SESEmailTemplate:
    def __init__(self, template_name: str, region_name: str = "us-east-1") -> None:
        self.name = template_name
        self.region = region_name
        self.client = boto3.Session().client(service_name="ses")

    def send(
        self,
        from_addr: str,
        recipients: list[str],
        replyto_list: list[str],
        data: dict[str, str],
        cc_list: list[str] | None = None,
        bcc_list: list[str] | None = None,
    ) -> None:
        destination = self._get_destination(recipients, cc_list, bcc_list)
        self.client.send_templated_email(
            **{
                "Source": from_addr,
                "Destination": destination,
                "ReplyToAddresses": replyto_list,
                "Template": self.name,
                "TemplateData": json.dumps(data),
            }
        )

    def create(self, subject: str, text_content: str, html_content: str) -> None:
        self.client.create_template(
            **{
                "Template": {
                    "TemplateName": self.name,
                    "SubjectPart": subject,
                    "TextPart": text_content,
                    "HtmlPart": html_content,
                }
            }
        )

    def update(self, subject: str, text_content: str, html_content: str) -> None:
        self.client.update_template(
            **{
                "Template": {
                    "TemplateName": self.name,
                    "SubjectPart": subject,
                    "TextPart": text_content,
                    "HtmlPart": html_content,
                }
            }
        )

    def test_render(self, data: dict[str, str]) -> str:
        response = self.client.test_render_template(
            **{"TemplateName": self.name, "TemplateData": json.dumps(data)}
        )
        return response.get("RenderedTemplate")

    def _get_destination(
        self,
        recipients: list[str],
        cc_list: list[str] | None,
        bcc_list: list[str] | None,
    ) -> dict[str, list[str]]:
        destination: dict[str, list[str]] = {"ToAddresses": recipients}
        if cc_list is not None:
            destination.update({"CcAddresses": cc_list})
        if bcc_list is not None:
            destination.update({"BccAddresses": bcc_list})
        return destination
