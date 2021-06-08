::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: © Copyright 2020 HP Development Company, L.P.
:: SPDX-License-Identifier: GPL-2.0-only
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::: MAIN ::::::::::::::::::::::::::::::::::::::
@echo off

SETLOCAL ENABLEDELAYEDEXPANSION

ECHO.
ECHO ## PROJECT CONFIGURATIONS ##
CALL:PROJECT_INFORMATION

ECHO.
ECHO ## GIT REPOSITORIES CONFIGURATION ##
CALL:CREATE_NEW_GITHUB_REPOSITORY datasets
CALL:CREATE_NEW_GITHUB_REPOSITORY labels
CALL:CREATE_NEW_GITHUB_REPOSITORY models

ECHO.
ECHO ## BUCKET CONFIGURATION ##
ECHO storage: >> config.yaml
CALL:CREATE_NEW_BUCKET_WIZARD

ECHO.
ECHO ## CREATE REPOSITORY WITH CONFIGURATIONS ##
CALL:PUSH_CONFIG_REPOSITORY

ECHO.
ECHO If you want to start an ml-git project with these settings you can use:
ECHO.
ECHO ml-git clone %REPO_LINK%

GOTO :END
:::::::::::::::::::::::::::::::::::::: END MAIN ::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::: SUBROUTINES ::::::::::::::::::::::::::::::::::::::
:PROJECT_INFORMATION
   MKDIR mlgit-repository
   CD ./mlgit-repository
   git init > log.txt
   MKDIR .ml-git
   CD ./.ml-git
   ECHO. 2>config.yaml
   SET /p USERNAME="What is your github username? "
   SET /p GITHUB_BASE_URL="If you are working with github enterprise, type the enterprise url, if not press enter to continue [default:https://github.com]: "
   SET /p PROJECT_NAME="What is your project name? "
   SET /p ORGANIZATION_NAME="What is your organization name? [default: will create in the user account] "
   IF ["%ORGANIZATION_NAME%"]==[""] (
      SET ORGANIZATION_NAME=%USERNAME%
      SET REPO_OWNER=/user/repos
   ) ELSE (
      SET REPO_OWNER=/orgs/%ORGANIZATION_NAME%/repos
   )
   IF ["%GITHUB_BASE_URL%"]==[""] (
      SET GITHUB_API_URL=https://api.github.com
      SET GITHUB_BASE_URL=https://github.com
   ) ELSE (
      SET GITHUB_API_URL=%GITHUB_BASE_URL%/api/v3
   )
   EXIT /B 0


:CREATE_NEW_GITHUB_REPOSITORY
   SET ENTITY_TYPE=%1
   SET /p yn="Do you want to create a remote repository for %ENTITY_TYPE%? (Y/n) "
   IF ["%yn%"]==[""] (
      SET yn=Y
   )
   SET REPO_NAME=%PROJECT_NAME%-mlgit-%ENTITY_TYPE%
   IF /i ["%yn:~0,1%"]==["Y"] (
      SET /p INPUT_REPO_NAME="What name do you want to give to your remote repo? [default: %REPO_NAME%] "
      IF NOT ["%INPUT_REPO_NAME%"]==[""] (
         SET REPO_NAME=%INPUT_REPO_NAME%
      )
      SET OUTPUT_FILE=log_%ENTITY_TYPE%_repository
      curl -H "Authorization: token %GITHUB_TOKEN%" %GITHUB_API_URL%%REPO_OWNER% -d "{\"name\": \"%REPO_NAME%\"}"
      SET REPO_LINK=%GITHUB_BASE_URL%/%USERNAME%/%REPO_NAME%
      ECHO Repository creation done. Go to !REPO_LINK! to see.
      ECHO %ENTITY_TYPE%: >> config.yaml
      ECHO   git: !REPO_LINK! >> config.yaml
   ) ELSE (
      IF /i ["%yn:~0,1%"]==["n"] (
         EXIT /B 0
      ) ELSE (
         ECHO Please answer Yes or no.
         CALL:CREATE_NEW_GITHUB_REPOSITORY %ENTITY_TYPE%
      )
   )
   EXIT /B 0


:CREATE_NEW_BUCKET

   SET /p STORE_TYPE="What type of storage do you want to configure? [s3h, azureblobh, minio]: "
   SET /p BUCKET_NAME="What name do you want to give to your bucket? "

   IF ["%STORE_TYPE%"]==["s3h"] (
      ECHO   %STORE_TYPE%: >> config.yaml
      ECHO     %BUCKET_NAME%: >> config.yaml

      aws s3api create-bucket --bucket %BUCKET_NAME% --region us-east-1
      ECHO       aws-credentials: >> config.yaml
      ECHO         profile: default >> config.yaml
   ) ELSE IF ["%STORE_TYPE%"]==["minio"] (
      SET /p ENDPOINT="What endpoint url connection to your bucket? "

      ECHO   s3h: >> config.yaml
      ECHO     %BUCKET_NAME%: >> config.yaml

      aws --endpoint-url !ENDPOINT! s3 mb s3://%BUCKET_NAME%
      ECHO       aws-credentials: >> config.yaml
      ECHO         profile: default >> config.yaml
      ECHO       endpoint-url: !ENDPOINT! >> config.yaml
   ) ELSE (
      ECHO   %STORE_TYPE%: >> config.yaml
      ECHO     %BUCKET_NAME%: >> config.yaml
      IF ["%STORE_TYPE%"]==["azureblobh"] (
         az storage container create -n %BUCKET_NAME%
         ECHO       credentials: None >> config.yaml
      ) ELSE (
         ECHO Please enter a valid storage type.
         CALL:CREATE_NEW_BUCKET
      )
   )
   EXIT /B 0


:CREATE_NEW_BUCKET_WIZARD
   SET /p yn="Do you want to create a new bucket? (Y/n) "
   IF ["%yn%"]==[""] (
      SET yn=Y
   )

   IF /i ["%yn:~0,1%"]==["Y"] (
      CALL:CREATE_NEW_BUCKET
      ECHO Bucket successfully created
      CALL:CREATE_NEW_BUCKET_WIZARD
   ) ELSE (
      IF /i ["%yn:~0,1%"]==["n"] (
         EXIT /B 0
      ) ELSE (
         ECHO Please answer Yes or no.
         CALL:CREATE_NEW_BUCKET_WIZARD
      )
   )
   EXIT /B 0


:PUSH_CONFIG_REPOSITORY
   SET REPO_NAME=%PROJECT_NAME%-mlgit-repository
   SET /p INPUT_REPO_NAME="What name do you want to give for the repository with these configurations? [default: %REPO_NAME%] "
   IF NOT ["%INPUT_REPO_NAME%"]==[""] (
      SET REPO_NAME=%INPUT_REPO_NAME%
   )
   git add config.yaml
   git commit -m "Initial commit with .ml-git configured"
   curl -H "Authorization: token %GITHUB_TOKEN%" %GITHUB_API_URL%%REPO_OWNER% -d "{\"name\": \"%REPO_NAME%\"}"
   SET str=%str:(Video)=%
   SET GITHUB_REPOSITORY_URL=https://%USERNAME%:%GITHUB_TOKEN%@%GITHUB_BASE_URL:https://=%/%ORGANIZATION_NAME%/%REPO_NAME%.git"
   git remote add origin %GITHUB_REPOSITORY_URL%
   git branch -M main
   git push --set-upstream origin main
   SET REPO_LINK=%GITHUB_BASE_URL%/%USERNAME%/%REPO_NAME%
   ECHO Repository creation done. Go to %REPO_LINK% to see.
   EXIT /B 0


:END
   PAUSE
   CD ../..
   RMDIR /S /Q mlgit-repository
   EXIT /B 0
