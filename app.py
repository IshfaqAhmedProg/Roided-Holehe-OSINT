#!/usr/bin/env python
# coding: utf-8

# In[48]:


import trio
import httpx
import pandas
import json
import os
import re
import logging
from datetime import datetime
from holehe.modules.crm.hubspot import hubspot
from holehe.modules.crm.amocrm import amocrm
from holehe.modules.crm.axonaut import axonaut
from holehe.modules.crm.insightly import insightly
from holehe.modules.crm.nimble import nimble
from holehe.modules.crm.nutshell import nutshell
from holehe.modules.crm.nocrm import nocrm
from holehe.modules.crm.pipedrive import pipedrive
from holehe.modules.crm.teamleader import teamleader
from holehe.modules.crm.zoho import zoho
from email_validator import validate_email, EmailNotValidError
from alive_progress import alive_bar
from pyfiglet import Figlet


async def main():
    logging.basicConfig(
        filename="ExceptionLogs.log",
        format="%(asctime)s %(message)s",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.debug("RoidedHolehe initialised!")
    __running__ = True
    while __running__:
        try:
            generateFiglet()
            input_file_path = getInputFilePath()
            emails = await getEmails(input_file_path)
            if len(emails) != 0:
                result = await runHolehe(emails)
                file_name = "\RoidedHoleheOutput" + getTimestamp() + ".xlsx"
                output_path = os.environ["USERPROFILE"] + "\Documents\RoidedHolehe"
                outputExcelFile(result, output_path, file_name)
            else:
                print(
                    "\x1B[31mNo emails found in file, please check if the emails in the file are valid!\x1B[37m"
                )
            __running__ = getYNInput("Do you want to restart? y/n")
        except Exception as exc:
            print("\x1B[31mErrorMain:", exc, "\x1B[37m")
            logger.error(exc)
        pass
    logger.debug("RoidedHolehe closed!")


def generateFiglet():
    f = Figlet(font="fender")
    print("\x1B[33m" + f.renderText("Roided Holehe") + "\x1B[32m")
    print("*-------------------Author---------------------*")
    print("\x1B[33mIshfaq Ahmed\x1B[32m, https://github.com/IshfaqAhmedProg")
    print("*------------------Based on--------------------*")
    print(
        "\x1B[33mHolehe OSINT\x1B[32m, https://github.com/megadose/holehe\x1B[37m\n\n\n\n"
    )


def getTimestamp():
    now = datetime.now()
    return now.strftime("%H%M%S%m%d%Y")


def getYNInput(message):
    invalid_input = True
    return_val = False
    while invalid_input:
        user_input = input(message)
        if bool(re.match(r"[YyNn]", user_input)):
            if bool(re.match(r"[Yy]", user_input)):
                return_val = True
                invalid_input = False
            elif bool(re.match(r"[Nn]", user_input)):
                return_val = False
                invalid_input = False
        else:
            print("\x1B[31mInvalid input! Please input either\x1B[37m y/n")
    return return_val


def outputExcelFile(data_to_write, file_path, file_name):
    result_dataframe = pandas.DataFrame(data_to_write)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print("\x1B[32mRoided Holehe directory created in:\x1B[37m", file_path)
    try:
        with pandas.ExcelWriter(file_path + file_name, engine="openpyxl") as writer:
            result_dataframe.to_excel(writer, "spreadsheet1")
            print("\n\n\x1B[32mOutput file saved to:\x1B[37m", file_path + file_name)
    except Exception as exc:
        raise Exception("\x1B[31mFailed to save output file!\x1B[37m", exc)


def getInputFilePath():
    file_invalid = True
    while file_invalid:
        print(
            "\x1B[32mEnter the path to the file containing the emails.(Should be a .xlsx file)\x1B[37m"
        )
        file_path = input("Path to your file:")
        print(file_path)
        if file_path.endswith(".xlsx"):
            file_invalid = False
        else:
            print("\x1B[31mNot a .xlsx file!\x1B[37m")
    if not (file_invalid):
        return file_path


async def getEmails(file_path):
    try:
        excel_data = pandas.read_excel(file_path)
    except Exception as exc:
        raise Exception("Error reading the file in " + file_path, exc)
    json_data = json.loads(excel_data.to_json())
    headers_in_file = list(json_data.keys())

    print("\x1B[32mSelect the index of the header the email address is in:\x1B[37m")
    for key in headers_in_file:
        print(headers_in_file.index(key), key)

    header_index = 0
    input_valid = False

    while input_valid == False:
        input_val = input("Index of the header:")
        if validateInput(input_val) and int(input_val) <= len(headers_in_file):
            input_valid = True
            header_index = int(input_val)
        else:
            print(
                "\x1B[31mInvalid input! make sure you select the index from the list!\x1B[37m"
            )

    header = headers_in_file[header_index]
    print("\x1B[32mSelected header:\x1B[37m", header)
    print("\n\x1B[32mChecking all emails, please wait...\x1B[37m")
    emails = []
    possibleEmails = list(json_data[header].values())
    with alive_bar(
        len(possibleEmails), bar="filling", spinner="waves", force_tty=True
    ) as bar:
        for x in possibleEmails:
            if x is not None and emailIsValid(x):
                emails.append(x)
            bar()

    print(len(emails), "\x1B[32mEmails found!\x1B[37m\n")
    # print("selected emails", emails)
    return emails


async def runHolehe(emailArray):
    holehe_modules = [
        "hubspot",
        "amocrm",
        "axonaut",
        "insightly",
        "nimble",
        "nutshell",
        "nocrm",
        "pipedrive",
        "teamleader",
        "zoho",
    ]
    try:
        result = []
        for module in holehe_modules:
            with alive_bar(
                len(emailArray), force_tty=True, bar="filling", spinner="waves"
            ) as bar:
                bar.title = "\x1B[32mVerifying on \x1B[37m" + module
                for email in emailArray:
                    bar.message = "Checking email " + email
                    client = httpx.AsyncClient()
                    out = []
                    await holeheSelector(module, email, client, out)
                    out[0]["emailaddress"] = email
                    result.append(out[0])
                    await client.aclose()
                    bar()
    except Exception as exc:
        raise Exception("An error has occured while running Holehe!", exc)
    else:
        # print(result)
        return result


async def holeheSelector(module, email, client, out):
    match module:
        case "hubspot":
            return await hubspot(email, client, out)
        case "amocrm":
            return await amocrm(email, client, out)
        case "axonaut":
            return await axonaut(email, client, out)
        case "insightly":
            return await insightly(email, client, out)
        case "nimble":
            return await nimble(email, client, out)
        case "nutshell":
            return await nutshell(email, client, out)
        case "nocrm":
            return await nocrm(email, client, out)
        case "pipedrive":
            return await pipedrive(email, client, out)
        case "teamleader":
            return await teamleader(email, client, out)
        case "zoho":
            return await zoho(email, client, out)


def emailIsValid(email):
    try:
        validation = validate_email(email, check_deliverability=True)
        email = validation.ascii_email
        return True
    except EmailNotValidError as e:
        print("\x1B[31m" + str(e) + " Check email:\x1B[37m", email)
        return False


def validateInput(input):
    try:
        val = int(input)
        return True
    except ValueError:
        try:
            val = float(input)
            return False
        except ValueError:
            return False


trio.run(main)


# In[ ]:


get_ipython().system('jupyter nbconvert --to script app.ipynb')


# In[47]:


get_ipython().system('pyinstaller app.py --collect-all pyfiglet --collect-data grapheme')

