from jenkins import Jenkins
from collections import Counter
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pandas import ExcelWriter, DataFrame
from tkinter import Label, Entry, Button, Tk, Frame
import tkinter.messagebox as tm
import re

class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)

        self.label_username = Label(self, text="Username")
        self.label_password = Label(self, text="Password")

        self.entry_username = Entry(self)
        self.entry_password = Entry(self, show="*")

        self.label_username.grid(row=0, column=1)
        self.label_password.grid(row=1, column=1)
        self.entry_username.grid(row=0, column=2)
        self.entry_password.grid(row=1, column=2)

        self.logbtn = Button(self, text="Login", command=self.main_process)
        self.logbtn.grid(row=2, column=1, columnspan=2)

        self.pack()

    def main_process(self):

        print("Jenkins Version Extractor")

        uname = self.entry_username.get()
        pword = self.entry_password.get()

        server = Jenkins('https://jenkins_url', username=uname, password=pword)
        user = server.get_whoami()
        version = server.get_version()

        #Environments list
        environmentReArrange = ['-DeployToEnvList']


        #to traverse package names list
        pkgTraverse = 0

        version_list = []
        #Append the new list of version values to version_list
        versionsAll = []

        #To keep track of the values in the list
        count = 0

        def firstVersionExtractor(server, environmentReArrange, count):

            firstAllInfo = server.get_job_info("folder_1",depth=2)

            firstAllJobs = firstAllInfo['jobs']
            #To fetch number of jobs under CBMA
            numOfJobs = len(firstAllJobs)

            for j in range(0,numOfJobs):
                try:
                    version_list.append([])

                    firstSpecficJob = firstAllJobs[j]['jobs']

                    firstSpecificName = firstSpecficJob[0]['name']

                    cutPosition = firstSpecificName.find('-')
                    firstSpecificName = firstSpecificName[cutPosition+1:]

                    versionsAll.append(firstSpecificName)

                    for everyJob in firstSpecficJob:
                        for envValue in environmentReArrange:
                            try:
                                if re.search(envValue, everyJob['name']):
                                    last_successful_build = everyJob['lastSuccessfulBuild']

                                    #Checking if the env has any successful builds
                                    if last_successful_build == None:
                                        versionsAll.append('N/A')
                                        continue
                                    #If it has, then take the number
                                    last_successful_build_number = last_successful_build['number']
                                    print(everyJob['fullName'])
                                    build_info = server.get_build_info(everyJob['fullName'], last_successful_build_number)
                                    display_info = build_info['displayName']
                                    cutPosition = display_info.find('-')
                                    display_info = display_info[cutPosition + 1:]
                                    versionsAll.append(display_info)
                            except IndexError:
                                continue

                    #Assign the list to the main and clear the values in it here.
                    print(versionsAll)
                    for k in versionsAll:
                        version_list[count].append(k)
                    versionsAll.clear()
                    count += 1

                except KeyError:
                    continue

            return count

        #For cleaning up the single build objects.

        def listCleaner(version_list,s):
            while s == "clean":
                true_list = []
                for vclean in version_list:
                    # notApplicableCleaner(vclean)
                    if (vclean == []):
                        version_list.remove(vclean)
                    countNotApp = Counter(vclean)
                    if ((countNotApp['N/A']) > 7):
                        version_list.remove(vclean)

                    if (len(vclean) == 1):
                        version_list.remove(vclean)
                        true_list.append(0)
                    else:
                        true_list.append(1)
                cleanCounter = Counter(true_list)
                if (cleanCounter[0] == 0):
                    s = "noCleaning"


        #Function Calls
        print("Starting First Job")
        nxtCount = cbmaVersionExtractor(server, environmentReArrange, count)
        print("First Job DONE")

        print("Clean-Up of the Elements")

        listCleaner(version_list,s="clean")

        print(version_list)
        df = DataFrame(version_list, columns=['Application Name', 'EnvironmentList'])

        print(df)

        writer = ExcelWriter('Version.xlsx')
        df.to_excel(writer, 'Versions', index=False)
        writer.save()

        tm.showinfo("Jenkins Version", "Excel Ready")


root = Tk()
root.title("Jenkins Version")
root.geometry("400x200")
lf = LoginFrame(root)
root.mainloop()
