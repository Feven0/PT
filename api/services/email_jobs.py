import os, sys

import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd

from .pathfig import *
    
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))


class RecommendationEmail:
    def __init__(self) -> None:
        self.bucket_name = 'auto-job-recommendation'
        
    def job_alert_email(self,RECIPIENT: str, name: str, message: list):
        SENDER = "10 Academy Training Team <train@10academy.org>"

        AWS_REGION = "us-east-1"

        SUBJECT = "10 Academy Job Match Alert"

        BODY_HTML = f"""
        <html>
            <body style="background-color:rgb(250, 235, 235)">
                <table align="center" border="0" cellpadding="0" cellspacing="0"
                    width="550" bgcolor="white" style="border:0px ">
                    <tbody style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;">
                    
                        
                        
                        <tr>
                        
                            <td align="center" style="background-color: #F5222D;
                                    height: 50px;">

                                <a href="#" style="text-decoration: none; color:white; font-weight: bolder;font-size: 20px;" >
                                    
                                            10 Academy
                                    
                                </a>
                            </td>
                                    
                        </tr>
                        
                        <tr style="height: 50px;">
                            <td align="center" style="border: none;
                                    border-bottom: 2px solid #F5222D; 
                                    padding-right: 20px; padding-bottom: 20px; padding-left:20px">
            
                                <p style="font-weight: bolder;font-size: 20px;
                                        letter-spacing: 0.025em;
                                        color:black;">
                                    <br> Jobs we found that matched to your profile
                                </p>
                            </td>
                        </tr>
            
                        <tr style="display: inline-block; color:black;">
                            <td style="height: 150px;
                                    padding: 20px;
                                    border: none; 
                                    border-bottom: 2px solid #361B0E;
                                    background-color: white;">
                                
                                <h2 style="text-align: left;
                                        align-items: center; color:black;">
                                    Dear {name}
                            </h2>
                                <p class="data"
                                style="text-align: justify-all;
                                        align-items: center; 
                                        font-size: 18px;
                                        color:black;
                                        padding-bottom: 12px;">
                                
                                You've been matched with some open jobs
                                </p>
                                <p class="data"
                                style="text-align: justify-all;
                                    align-items: center; 
                                    font-size: 20px;
                                    color:black;
                                    padding-bottom: 12px;">
                                    {message}
                                </p>
                            </td>
                        </tr>
                    


                    </tbody>
                </table>
            </body>
            </html>
        """
        CHARSET = "UTF-8"

        client = boto3.client("ses", region_name=AWS_REGION)

        msg = MIMEMultipart("mixed")
        # Add subject, from and to lines.
        msg["Subject"] = SUBJECT
        msg["From"] = SENDER
        msg["To"] = RECIPIENT

        # Create a multipart/alternative child container.
        msg_body = MIMEMultipart("alternative")

        # Encode the text and HTML content and set the character encoding. This step is
        # necessary if you're sending a message with characters outside the ASCII range.
        # textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
        htmlpart = MIMEText(BODY_HTML.encode(CHARSET), "html", CHARSET)

        # Add the text and HTML parts to the child container.
        # msg_body.attach(textpart)
        msg_body.attach(htmlpart)

        # Attach the multipart/alternative child container to the multipart/mixed
        # parent container.
        msg.attach(msg_body)

        try:            
            response = client.send_raw_email(
                Source=SENDER,
                Destinations=[RECIPIENT],
                RawMessage={
                    "Data": msg.as_string(),
                },
            )
        except ClientError as e:
            logger.error(e.response["Error"]["Message"])
        else:
            logger.good(f'Email sent to {name}! Message ID: {response["MessageId"]}'),

    def get_email_job_alert(self, df):
        if df.empty:
            return {}

        email_messages = {}
        for _, row in df.iterrows():
            email = row['Email']
            if email in email_messages:
                email_messages[email].append(f"<li>{row['company']} is looking for a {row['title']}. <br><span style='color:red;'>Apply here: {row['post_link']}</li>")
            else:
                email_messages[email] = []
                email_messages[email].append(f"<li>{row['company']} is looking for a {row['title']}.<br> <span style='color:red;'>Apply here: {row['post_link']}</li>")

        return email_messages
            
    def send_recommendation_email(self, recommend_df):
        # recommend_df = get_recommendation_details()
        
        df_messages = self.get_email_job_alert(recommend_df)
        if recommend_df.empty or df_messages == {}:
            return

        for email, message_list in df_messages.items():
            name = recommend_df[recommend_df['Email'] == email]['Name'].iloc[0]
            if email in df_messages:
                self.job_alert_email(email, name, "<br>".join(message_list))
                
if __name__ == "__main__":
    obj = RecommendationEmail()
    # obj.send_recommendation_email()