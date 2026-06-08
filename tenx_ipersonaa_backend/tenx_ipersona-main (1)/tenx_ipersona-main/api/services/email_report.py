
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from botocore.exceptions import ClientError
import boto3
import pandas as pd
from curses.ascii import EM
import os
import sys

from .pathfig import *
    

from api.utils.logger import LLPackerLogger


logger = LLPackerLogger(os.path.basename(__file__))



class ReportMail:

    def __init__(self) -> None:

        self.bucket_name = 'auto-job-recommendation'
        


    def report_email(self, RECIPIENT: str, name: str, message: list):
        SENDER = "10 Academy Training Team <train@10academy.org>"

        AWS_REGION = "us-east-1"

        SUBJECT = "10 Academy Job Match Alert"

        BODY_HTML = f"""
                        <html>
                    <body style="background-color:rgb(250, 235, 235); color:black;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0"
                            width="550" bgcolor="white" style="border:0px">
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
                    
                                        <p style="font-weight: bolder;font-size: 38px;
                                                letter-spacing: 0.025em;
                                                ">
                                             Checkout latest Job sent to trainees
                                        </p>
                                    </td>
                                </tr>
                    
                                <tr style="display: inline-block;">
                                    <td style="height: 150px;
                                            padding: 20px;
                                            border: none; 
                                            border-bottom: 2px solid #361B0E;
                                            background-color: white;">
                                        
                                        
                                        
                                    
                                        <p class="data"
                                        style="text-align: justify-all;
                                            align-items: center; 
                                            font-size: 18px;
                                            padding-bottom: 12px;">
                                            Jobs sent to trainees:
                                        </p>
                                        <p>
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
            # Provide the contents of the email.
            response = client.send_raw_email(
                Source=SENDER,
                Destinations=[RECIPIENT],
                RawMessage={
                    "Data": msg.as_string(),
                },
            )
            print(f"Sent to {name}")
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response["Error"]["Message"])
        else:
            print("Email sent! Message ID:"),
            print(response["MessageId"])

    def get_team_df(self):
        team_df = pd.DataFrame(
            {
                "Name": [
                    # "Arun",
                    "yabebal",
                   
                    # "Bereket Kibru",
              
                    # "Mesfine",
              
                    #"Mahlet",
                    #"Tegisty"

                ],
                "Email": [
                    # "arun@10academy.org",
                    "yabebal@10academy.org",
             
                    # "bereket@10academy.org",
               
                    # "mesfin@10academy.org",
               
                    #"mahlet@10academy.org",
                    #"tegisty@10academy.org"

                ],
            }
        )
        return team_df
    
    def send_email(self, df):
        
        team_df = self.get_team_df()
        # df = get_recommendation_details()    
          
        if isinstance(df, type(None)) or df.empty:
            pass
        else:
            email_contents = {row["Email"]: [] for _, row in team_df.iterrows()}
            
            processed_trainees = set()
            
            for _, trainee_row in df.iterrows():
                trainee_name = trainee_row["Name"]
                if trainee_name in processed_trainees:
                    continue 
                processed_trainees.add(trainee_name)
                
                trainee_email_content = f"Jobs sent for trainee <b>{trainee_name}</b>:"
                for _, trainee_row in df[df["Name"] == trainee_name].iterrows():
                    company = trainee_row["company"]
                    title = trainee_row["title"]
                    trainee_email_content += f"<li><b>{company}</b> company for <b>{title}</b> position.</li>"
                
                for team_member_email in email_contents:
                    email_contents[team_member_email].append(trainee_email_content)
            
            for team_member_email, trainee_email_contents in email_contents.items():
                name = team_df[team_df["Email"] == team_member_email]["Name"].iloc[0]
                email_content = "".join(trainee_email_contents)
                self.report_email(team_member_email, name, email_content)
                
if '__main__' == __name__:

    obj = ReportMail()
    # df =  obj.send_email()