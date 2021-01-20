import re # regex
import datetime as datetime

# google APIs
from googleapiclient.discovery import build
from google.oauth2 import service_account



class Schedule:
    
    # constructor
    def __init__(self, spreadsheet_id, spreadsheet_range, current_date):
        self.__spreadsheet_id = spreadsheet_id
        self.__spreadsheet_range = spreadsheet_range
        self.__curr_date = current_date
        self.__curr_column = None
        self.__values = None
        
        self.updateSpreadsheet()
    
    
    # update spreadsheet
    # this function is created base on video:
    # https://www.youtube.com/watch?v=4ssigWmExak
    def updateSpreadsheet(self):
        # credential file
        SERVICE_ACCOUNT_FILE = "credential_key.json"
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        
        # create credential w/ file
        creds = None
        creds = service_account.Credentials.from_service_account_file(
                        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # spreadsheet ID
        # SAMPLE_SPREADSHEET_ID = "1FUdVpQe8WYOcYyFWFrbVJSvhVwqskRGL_8kYZCfgci4"
        SAMPLE_SPREADSHEET_ID = self.__spreadsheet_id
        
        # open spreadsheet
        service = build("sheets", "v4", credentials=creds)
        
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=self.__spreadsheet_range).execute()
        
        # get 2d arr from spreadsheets
        self.__values = result.get("values", [])
        
        self.__find_curr_year_column()
    
    
    # getters
    
    def getSpreadsheetID(self):
        return self.__spreadsheet_id
    
    def getSpreadsheetRange(self):
        return self.__spreadsheet_range
    
    def getCurrColumn(self):
        if self.__curr_column != None:
            return self.__curr_column
        else: return None
    
    def getCurrDate(self):
        if self.__curr_date != None:
            return self.__curr_date
        else: return None
    
    def getCurrYear(self):
        if self.__curr_year != None:
            return self.__curr_year
        else: return None
    
    # setter
    
    def setCurrDate(self, date):
        if date != None:
            self.__curr_date = date
            self.__find_curr_year_column()
    
    
    
    # private: find current year & next column (date)
    def __find_curr_year_column(self):
        self.__curr_year = ""
        last_date = self.__curr_date
        
        year_indicator = "year="
        
        # find year indicator in values
        empty_flag = True
        stop_checking_date_flag = False
        for i in self.__values:
            match_flag = None
            try:
                match_flag = re.match(year_indicator, i[0])
                if match_flag != None:
                    self.__curr_year = str(i)[7:11]
                empty_flag = False
            except: # skip empty line, do nothing
                empty_flag = True
            
            # update curr date buffer
            
            check_date_flag = empty_flag != True and stop_checking_date_flag == False and match_flag == None and i[0][0].isdigit() and self.__curr_year != None
            
            if check_date_flag:
                temp_date = datetime.datetime.strptime(self.__curr_year+'/'+i[0], "%Y/%m/%d")
                if temp_date.date() < self.__curr_date.date():
                    last_date = temp_date
                elif temp_date.date() >= self.__curr_date.date():
                    self.__curr_column = i
                    stop_checking_date_flag = True