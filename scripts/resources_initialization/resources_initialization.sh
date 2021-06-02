#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

################################ SUBROUTINES ###################################

create_new_github_repository()
{
   ENTITY_TYPE=$1
   read -p "Do you want to create a remote repository for ${ENTITY_TYPE}? (Y/n) " yn

   if [ -z "${yn}" ]
   then
      yn="Yes"
   fi
   case ${yn} in
      [Yy]* ) REPO_NAME="${PROJECT_NAME}-mlgit-${ENTITY_TYPE}";
              read -p "What name do you want to give to your remote repo? [default: ${REPO_NAME}] " INPUT_REPO_NAME;
              if ! [ -z "${INPUT_REPO_NAME}" ]
              then
                 REPO_NAME=${INPUT_REPO_NAME}
              fi
              OUTPUT_FILE=log_${ENTITY_TYPE}_repository
              HTTP_CODE=$(curl -s -o ../../${OUTPUT_FILE} -w "%{http_code}" -H "Authorization: token ${GITHUB_TOKEN}" ${GITHUB_API_URL}${REPO_OWNER} -d "{\"name\": \"${REPONAME:-${REPO_NAME}}\"}")
              if [[ HTTP_CODE -ne 201 ]]; then
                 echo "Could not create the repository, please see ${OUTPUT_FILE} for more information."
                 clear_workspace_and_exit
              else
                 REPO_LINK=${GITHUB_BASE_URL}/${USERNAME}/${REPO_NAME}
                 echo "Repository creation done. Go to ${REPO_LINK} to see."
                 echo "${ENTITY_TYPE}:" >> config.yaml
                 echo "  git: ${REPO_LINK}" >> config.yaml
              fi;;
      [Nn]* ) return;;
      * ) echo "Please answer Yes or no."; create_new_github_repository ${ENTITY_TYPE};;
   esac
}


create_new_bucket()
{
   read -p "What type of storage do you want to configure? [s3h, azureblobh, minio]: " STORE_TYPE
   read -p "What name do you want to give to your bucket? " BUCKET_NAME
   read -p "What endpoint url connection to your bucket? " ENDPOINT
   
   {
   if [ "${STORE_TYPE}" == "s3h" ];
   then
      echo "  ${STORE_TYPE}:" >> config.yaml
      echo "    ${BUCKET_NAME}:" >> config.yaml

      aws s3api create-bucket --bucket ${BUCKET_NAME} --region us-east-1
      echo "      aws-credentials:" >> config.yaml
      echo "        profile: default" >> config.yaml
   elif [ "${STORE_TYPE}" == "minio" ];
   then
      echo "  s3h:" >> config.yaml
      echo "    ${BUCKET_NAME}:" >> config.yaml

      aws --endpoint-url ${ENDPOINT} s3 mb s3://${BUCKET_NAME}
      echo "      aws-credentials:" >> config.yaml
      echo "        profile: default" >> config.yaml
      echo "      endpoint-url: " ${ENDPOINT} >> config.yaml
   elif [ "${STORE_TYPE}" == "azureblobh" ];
   then
      echo "  ${STORE_TYPE}:" >> config.yaml
      echo "    ${BUCKET_NAME}:" >> config.yaml

      az storage container create -n ${BUCKET_NAME}
      echo "      credentials: None" >> config.yaml
   else
      echo "Please enter a valid storage type."
      create_new_bucket
   fi
   } > log.txt
}


create_new_bucket_wizard()
{
   read -p "Do you want to create a new bucket? (Y/n) " yn

   if [ -z "${yn}" ]
   then
      yn="Yes"
   fi
   case ${yn} in
      [Yy]* ) create_new_bucket;
              echo "Bucket successfully created"
              create_new_bucket_wizard;;
      [Nn]* ) return;;
      * ) echo "Please answer Yes or no."; create_new_bucket_wizard;;
   esac
}


create_clone_repository_folder()
{
  {
   rm -rf ./mlgit-repository
   mkdir ./mlgit-repository && cd ./mlgit-repository
   git init
   mkdir ./.ml-git && cd ./.ml-git
   touch config.yaml
   } > /dev/null
}


push_config_repository()
{
   REPO_NAME="${PROJECT_NAME}-mlgit-repository"
   read -p "What name do you want to give for the repository with these configurations? [default: ${REPO_NAME}] " INPUT_REPO_NAME;
   git add config.yaml
   git commit -m "Initial commit with .ml-git configured"
   if ! [ -z "${INPUT_REPO_NAME}" ]
   then
     REPO_NAME=${INPUT_REPO_NAME}
   fi
   OUTPUT_FILE=log_clone_repository
   HTTP_CODE=$(curl -s -o ../../$OUTPUT_FILE -w "%{http_code}" -H "Authorization: token ${GITHUB_TOKEN}" ${GITHUB_API_URL}${REPO_OWNER} -d "{\"name\": \"${REPONAME:-$REPO_NAME}\"}")
   if [[ HTTP_CODE -ne 201 ]]; then
      echo "Could not create the repository, please see $OUTPUT_FILE for more information."
      clear_workspace_and_exit
   else
      GITHUB_REPOSITORY_URL="https://${USERNAME}:${GITHUB_TOKEN}@${GITHUB_BASE_URL//'https://'}/${ORGANIZATION_NAME}/${REPO_NAME}.git"
      git remote add origin ${GITHUB_REPOSITORY_URL}
      git branch -M main
      git push --set-upstream origin main
      REPO_LINK=${GITHUB_BASE_URL}/${USERNAME}/${REPO_NAME}
      echo "Repository creation done. Go to $REPO_LINK to see."
   fi
}


clear_workspace_and_exit(){
   cd ../.. && rm -rf ./mlgit-repository
   exit 0
}

project_information(){
   read -p "What is your github username? " USERNAME
   read -p "If you are working with github enterprise, type the enterprise url, if not press enter to continue [default:https://github.com]: " GITHUB_BASE_URL
   read -p "What is your project name? " PROJECT_NAME
   read -p "What is your organization name? [default: will create in the user account] " ORGANIZATION_NAME
   if [ -z "$ORGANIZATION_NAME" ]
   then
      ORGANIZATION_NAME=${USERNAME}
      REPO_OWNER="/user/repos"
   else
      REPO_OWNER="/orgs/${ORGANIZATION_NAME}/repos"
   fi
   if [ -z "$GITHUB_BASE_URL" ]
   then
      GITHUB_API_URL="https://api.github.com"
      GITHUB_BASE_URL="https://github.com"
   else
      GITHUB_API_URL=${GITHUB_BASE_URL}/api/v3
   fi
}
############################## END SUBROUTINES #################################

#################################### MAIN ######################################
echo -e "\n## PROJECT CONFIGURATIONS ##"
create_clone_repository_folder
project_information


echo -e "\n## GIT REPOSITORIES CONFIGURATION ##"
create_new_github_repository dataset
create_new_github_repository labels
create_new_github_repository model

echo -e "\n## BUCKET CONFIGURATION ##"
echo "storage:" >> config.yaml
create_new_bucket_wizard

echo -e "\n## CREATE REPOSITORY WITH CONFIGURATIONS ##"
push_config_repository
echo -e "\nIf you want to start an ml-git project with these settings you can use:\n\tml-git clone $REPO_LINK"

clear_workspace_and_exit

################################## END MAIN ####################################
