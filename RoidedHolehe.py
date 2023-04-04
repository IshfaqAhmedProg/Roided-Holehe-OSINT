#!/usr/bin/env python
# coding: utf-8

# In[3]:


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
from alive_progress import alive_bar
from pyfiglet import Figlet
from collections import defaultdict


async def main():
    # Initialising Logger
    logging.basicConfig(
        filename="ExceptionLogs.log",
        format="%(asctime)s %(message)s",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # Message on startup
    logger.debug("RoidedHolehe initialised!")
    # Flag to check if program is running or not
    __running__ = True
    while __running__:
        try:
            generateFiglet()
            # Get the input file path
            input_file_path = getInputFilePath()
            emails = await getEmails(input_file_path)
            if len(emails) != 0:
                # Run the emails through holehe OSINT and turn to dict as it returns defaultdict
                result = dict(await runHolehe(emails))
                # unique by timestamp output file name
                output_file_name = (
                    "\RoidedHoleheOutput"
                    + datetime.now().strftime("%H%M%S%m%d%Y")
                    + ".xlsx"
                )
                output_path = os.environ["USERPROFILE"] + "\Documents\RoidedHolehe"
                data_to_write = await createDataframe(result)
                outputExcelFile(data_to_write, output_path, output_file_name)
            else:
                print(
                    "\x1B[31mNo emails found in file, please check if the emails in the file are valid!\x1B[37m"
                )
            __running__ = askYNQuestion("Do you want to restart? y/n: ")
        except Exception as exc:
            print("\x1B[31mErrorMain:", exc, "\x1B[37m")
            logger.error(exc)
        pass
    logger.debug("RoidedHolehe closed!")


async def getEmails(file_path):
    try:
        # Get the data from file
        if file_path.endswith(".csv"):
            excel_data = pandas.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            excel_data = pandas.read_excel(file_path)
    except Exception as exc:
        raise Exception("Error reading the file in " + file_path, exc)
    # Convert to json data
    json_data = json.loads(excel_data.to_json())
    # get the headers in the file
    headers_in_file = list(json_data.keys())

    # Print out the headers and ask user to select a header
    print("\x1B[32mSelect the index of the header the email address is in:\x1B[37m")
    for header in headers_in_file:
        print(headers_in_file.index(header), header)

    header_index = 0
    input_valid = False

    while input_valid == False:
        input_val = input("Index of the header:")
        # check if user input is less than length of the header array and if the value is integer
        if inputIsInt(input_val) and int(input_val) <= len(headers_in_file):
            input_valid = True
            header_index = int(input_val)
        else:
            print(
                "\x1B[31mInvalid input! make sure you select the index from the list!\x1B[37m"
            )
    # Display the selected header to the user
    header = headers_in_file[header_index]
    print("\x1B[32mSelected header:\x1B[37m", header)
    print("\n\x1B[32mChecking all emails, please wait...\x1B[37m")
    emails = []
    possibleEmails = list(json_data[header].values())
    with alive_bar(
        len(possibleEmails), bar="filling", spinner="waves", force_tty=True
    ) as bar:
        # Checking if the user input emails are actually emails or not
        for email in possibleEmails:
            # Simple regex to check email, more complex regex not used as TTR is very high for lot of emails
            matches_regex = bool(re.match(r"^(.+)@(.+)$", str(email)))
            if email is not None and matches_regex:
                emails.append(email)
            bar()

    # Printing out the number of emails found
    print(len(emails), "\x1B[32mEmails found!\x1B[37m\n")
    return emails


async def runHolehe(emailArray):
    # to add new modules add them here and on holeheSelector()
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
        final_result = defaultdict(dict)
        for module in holehe_modules:
            # call progress bar hook
            with alive_bar(
                len(emailArray), force_tty=True, bar="filling", spinner="waves"
            ) as bar:
                bar.title = "\x1B[32m\nVerifying on \x1B[37m" + module
                for email in emailArray:
                    bar.message = "Checking email " + email

                    # http client to run holehe
                    client = httpx.AsyncClient()
                    holehe_results = []
                    await holeheSelector(module, email, client, holehe_results)
                    module_result = {
                        "Exists": holehe_results[0]["exists"],
                        "Rate Limit": not holehe_results[0]["rateLimit"],
                    }
                    final_result[email][module] = module_result

                    # close http client after running holehe
                    await client.aclose()

                    # update progress bar
                    bar()
    except Exception as exc:
        raise Exception("An error has occured while running Holehe!", exc)
    else:
        return final_result


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


async def createDataframe(data_to_format):
    # converting from this

    # {
    #     "A": {
    #         "a": {"Exists": False, "RateLimit": False},
    #         "b": {"Exists": False, "RateLimit": False},
    #     },
    #     "B": {
    #         "a": {"Exists": False, "RateLimit": False},
    #         "b": {"Exists": False, "RateLimit": False},
    #     },
    # }

    # to this

    #     a                 b
    #     Exists RateLimit Exists RateLimit
    # A   False      False  False     False
    # B   False      False  False     False

    # Create defaultdict to store the data
    temp_dict = defaultdict(dict)

    # Loop through the dictionary and extract the data
    for email, module in data_to_format.items():
        for key, value in module.items():
            temp_dict[email][key + " - " + "Exists"] = value["Exists"]
            temp_dict[email][key + " - " + "Rate Limit"] = value["Rate Limit"]

    # Convert the defaultdict to a DataFrame
    dataframe = pandas.DataFrame.from_dict(temp_dict, orient="index")

    # Rename the column headers
    dataframe.columns = pandas.MultiIndex.from_tuples(
        [tuple(col.split(" - ")) for col in dataframe.columns]
    )

    return dataframe


def outputExcelFile(data_to_write, file_path, file_name):
    # Create output directory if it doesnt exist
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print("\x1B[32mRoided Holehe directory created in:\x1B[37m", file_path)
    try:
        # writing to excel file using openpyxl
        with pandas.ExcelWriter(file_path + file_name, engine="openpyxl") as writer:
            data_to_write.to_excel(
                writer,
                "spreadsheet1",
            )
            print("\n\n\x1B[32mOutput file saved to:\x1B[37m", file_path + file_name)
    except Exception as exc:
        raise Exception("\x1B[31mFailed to save output file!\x1B[37m", exc)


# Utility functions


def askYNQuestion(message):
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


def generateFiglet():
    f = Figlet(font="fender")
    print("\x1B[33m" + f.renderText("Roided Holehe") + "\x1B[32m")
    print("*-------------------Author---------------------*")
    print("\x1B[33mIshfaq Ahmed\x1B[32m, https://github.com/IshfaqAhmedProg")
    print("*------------------Based on--------------------*")
    print(
        "\x1B[33mHolehe OSINT\x1B[32m, https://github.com/megadose/holehe\x1B[37m\n\n\n\n"
    )


def getInputFilePath():
    file_invalid = True
    while file_invalid:
        print(
            "\x1B[32mEnter the path to the file containing the emails.(Should be a .xlsx file)\x1B[37m"
        )
        file_path = input("Path to your file:")
        print(file_path)
        # Check if xlsx or csv file or none
        if file_path.endswith(".xlsx") or file_path.endswith(".csv"):
            file_invalid = False
        else:
            print("\x1B[31mNot a csv or xlsx file!\x1B[37m")
    if not (file_invalid):
        return file_path


def inputIsInt(input):
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

