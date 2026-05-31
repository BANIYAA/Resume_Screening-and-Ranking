import pandas as pd
import io
import os

# 1. Ensure the master Excel file exists
excel_path = "Screening_Rules.xlsx"
if not os.path.exists(excel_path):
    print(f"Error: {excel_path} not found. Please ensure it is in the same folder.")
    exit()

# 2. Define the new role data
new_roles_data = {
    "Frontend_Developer": """Keyword,Category,Weight,Synonyms
javascript,Programming,10,"js, vanilla js, es6, ecmascript"
react,Frameworks,10,"reactjs, react.js, react native"
typescript,Programming,9,"ts, type script"
html,Fundamentals,6,"html5, markup"
css,Fundamentals,6,"css3, cascading style sheets"
tailwind,CSS Frameworks,7,"tailwind css, tailwindcss"
redux,State Management,7,"redux toolkit, rtk"
vue,Frameworks,7,"vuejs, vue.js"
angular,Frameworks,7,"angularjs, angular.js"
webpack,Build Tools,5,"web pack, module bundler"
jest,Testing,6,"jest testing, unit testing"
responsive design,Methodology,7,"mobile-first, mobile friendly"
""",

    "DevOps_Engineer": """Keyword,Category,Weight,Synonyms
aws,Cloud,10,"amazon web services, aws cloud"
kubernetes,Container Orchestration,10,"k8s"
docker,Containerization,9,"docker container, dockerfile"
terraform,IaC,9,"hashicorp terraform, infrastructure as code"
ci/cd,Methodology,8,"continuous integration, continuous deployment, continuous delivery"
jenkins,CI/CD Tools,7,"jenkins pipeline, jenkins ci"
linux,Operating Systems,8,"ubuntu, centos, unix, debian"
bash,Scripting,6,"shell scripting, bash script, shell"
ansible,Configuration Management,7,"ansible playbook"
prometheus,Monitoring,6,"prometheus monitoring"
grafana,Monitoring,6,"grafana dashboard"
azure,Cloud,8,"microsoft azure, azure devops"
""",

    "Product_Manager": """Keyword,Category,Weight,Synonyms
agile,Methodology,10,"agile methodology, agile framework, agile environment"
scrum,Methodology,9,"scrum master, sprints, scrum framework"
roadmapping,Strategy,8,"product roadmap, road-mapping"
jira,Tools,8,"atlassian jira"
a/b testing,Analytics,7,"split testing, ab testing"
user stories,Documentation,8,"user story mapping, acceptance criteria"
stakeholder management,Soft Skills,9,"stakeholder communication, stakeholder alignment"
go-to-market,Strategy,8,"gtm, go to market, launch strategy"
confluence,Tools,5,"atlassian confluence"
product strategy,Strategy,9,"product vision, product discovery"
data analysis,Analytics,7,"data driven, data-driven decisions"
kpi,Metrics,7,"key performance indicators, okrs, okr"
""",

    "ML_Engineer": """Keyword,Category,Weight,Synonyms
python,Programming,10,"python3, python 3"
tensorflow,Frameworks,9,"tf, tensor-flow"
pytorch,Frameworks,9,"torch"
scikit-learn,Libraries,8,"sklearn, scikit learn"
nlp,Domain,8,"natural language processing, text processing, llm"
computer vision,Domain,7,"cv, machine vision, image processing"
deep learning,Domain,9,"dl, neural networks, dnn"
mlops,Methodology,8,"machine learning operations, model deployment"
pandas,Data Libraries,7,"pandas library, pd"
spark,Big Data,7,"apache spark, pyspark"
sql,Databases,6,"mysql, postgresql"
hugging face,Libraries,7,"huggingface, transformers"
""",

    "Backend_Developer": """Keyword,Category,Weight,Synonyms
java,Programming,10,"java 8, java 11, java 17, core java"
spring boot,Frameworks,10,"springboot, spring-boot, spring framework"
microservices,Architecture,9,"micro-services, microservice architecture"
sql,Databases,8,"mysql, postgresql, postgres, oracle db"
rest api,Architecture,8,"restful, rest apis, restful api, restful web services"
hibernate,ORM,7,"jpa, java persistence api"
kafka,Messaging,7,"apache kafka, event driven"
docker,DevOps,6,"docker container, docker-compose"
kubernetes,DevOps,6,"k8s"
junit,Testing,6,"mockito, unit testing, integration testing"
maven,Build Tools,5,"gradle"
nosql,Databases,6,"mongodb, mongo db, cassandra"
"""
}

# 3. Append the new data to the Excel file
print("Updating Screening_Rules.xlsx...")

# We use mode='a' (append) and if_sheet_exists='replace' to safely add the tabs
with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    for role_name, csv_string in new_roles_data.items():
        # Convert the raw text string into a pandas DataFrame
        df = pd.read_csv(io.StringIO(csv_string.strip()))
        
        # Save it directly into the Excel workbook as a new sheet
        df.to_excel(writer, sheet_name=role_name, index=False)
        print(f" -> Added tab: {role_name}")

print("\nSuccess! All roles have been added to your Excel file.")