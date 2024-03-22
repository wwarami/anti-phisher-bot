import os
import sys
from src.database import AsyncDatabaseManager
from rich.console import Console
from src.cli.utils import print_banner, send_recheck_request_response_to_user


class CliManager:
    ri = Console()
    COMMANDS = """1- View urls
2- View recheck requests
3- Recheck a request
4- Start rechecking
5- Quit"""
    
    async def start(self):
        # Start the program
        os.system('clear')
        print_banner()
        while True:
            command = self.get_command()
            try:
                await self.parse_command(command)
            except KeyboardInterrupt:
                self.ri.print('\nCommand cancelled.', style='green bold')
                continue
            except Exception as ex:
                self.ri.print(f'Something went wrong while parsing your command. Detail: {ex}', style='red')
                break


    def get_command(self):
        self.ri.print(self.COMMANDS, style='white')
        self.ri.print('Select what you want to do: ', style='blue bold', end='')
        return input()


    async def parse_command(self, command: str):
        match command.strip():
            case '1':
                await self.view_urls()
            case '2':
                await self.view_recheck_requests()
            case '3':
                await self.recheck_a_request()
            case '4':
                await self.start_rechecking_requests()
            case '5':
                sys.exit()
            case _:
                self.ri.print('Not a valid command! Enter the command number please.', style='green bold')


    async def view_urls(self):
        self.ri.print('*View chechked urls (Use "ctrl + c" to cancel.): ', style='bold')
        
        while True:
            self.ri.print(' -Filter only valids or unvalids (Y: Valids, N: Unvalids, A: All):  ', end='')
            inp = input().capitalize().strip()
            if inp == 'Y':
                only_valids = True
                only_unvalids = False
                break
            elif inp == 'N':
                only_unvalids = True
                only_valids = False
                break
            elif inp == 'A':
                only_valids = False
                only_unvalids = False
                break
            else:
                self.ri.print('  *Please enter a valid character (Use "ctrl + c" to cancel.)', style="red bold")
        
        while True:
            self.ri.print(' -Filter only with or with out recheck request (Y: With, N: Without, A: All):  ', end='')
            inp = input().capitalize().strip()
            if inp == 'Y':
                only_with_recheck_request = True
                only_with_out_recheck_request = False
                break
            elif inp == 'N':
                only_with_out_recheck_request = True
                only_with_recheck_request = False
                break
            elif inp == 'A':
                only_with_recheck_request = False
                only_with_out_recheck_request = False
                break
            else:
                self.ri.print(' *Please enter a valid character (Use "ctrl + c" to cancel.)', style="red bold")
        # TODO: Date filtering will be implemented.
        
        urls = await AsyncDatabaseManager().get_urls(only_valids=only_valids,
                                                    only_unvalids=only_unvalids,
                                                    only_with_recheck_request=only_with_recheck_request,
                                                    only_with_out_recheck_request=only_with_out_recheck_request)
        self.ri.print(f"Url are fetched. Count: {len(urls)} ...", style='bold green')
        for url in urls:
            self.ri.print(url, style='blue bold')
        
        self.ri.print('Continue (All urls were fetched...): ', end='')
        input()


    async def view_recheck_requests(self):
        self.ri.print('*View recheck requests (Use "ctrl + c" to cancel.): ', style='bold')

        while True:
            self.ri.print(' -From user (Empty for none):  ', end='')
            inp = input().strip()
            if inp != '':
                from_user_id = inp
                break
            else:
                from_user_id = None
                break

        while True:
            self.ri.print(' -Filter only checked requests (Y: Checked, N: Not Checked, A: All):  ', end='')
            inp = input().capitalize().strip()
            if inp == 'Y':
                only_checked = True
                only_not_checked = False
                break
            elif inp == 'N':
                only_not_checked = True
                only_checked = False
                break
            elif inp == 'A':
                only_not_checked = False
                only_checked = False
                break
            else:
                self.ri.print('  *Please enter a valid character (Use "ctrl + c" to cancel.)', style="red bold")

        while True:
            self.ri.print(' -Filter only valid url requests (Y: Valids, N: Unvalids, A: All):  ', end='')
            inp = input().capitalize().strip()
            if inp == 'Y':
                only_new_valid = True
                only_new_unvalid = False
                break
            elif inp == 'N':
                only_new_unvalid = True
                only_new_valid = False
                break
            elif inp == 'A':
                only_new_unvalid = False
                only_new_valid = False
                break
            else:
                self.ri.print('  *Please enter a valid character (Use "ctrl + c" to cancel.)', style="red bold")
        
        # TODO: Date filtering will be implemented.
            
        recheck_request = await AsyncDatabaseManager().get_recheck_requests(from_user_id=from_user_id,
                                                                            only_checked=only_checked,
                                                                            only_not_checked=only_not_checked,
                                                                            only_new_valid=only_new_valid,
                                                                            only_new_unvalid=only_new_unvalid)
        
        self.ri.print(f"Recheck requests are fetched. Count: {len(recheck_request)} ...", style='bold green')
        for recheck_request in recheck_request:
            request_date_str = recheck_request.request_date.strftime("%m/%d/%Y, %H:%M:%S")
            checked_date_str = recheck_request.checked_date.strftime("%m/%d/%Y, %H:%M:%S") if recheck_request.checked_date else 'Not Checked Yet'
            self.ri.print(f"<UrlCheckRequest(id={recheck_request.id} ,url={recheck_request.url}, is_checked={recheck_request.is_checked}, new_result={recheck_request.new_is_valid}, request_date='{request_date_str}', checked_date='{checked_date_str}')>")

        self.ri.print('Continue (All recheck requests were fetched...): ', end='')
        input()


    async def recheck_a_request(self):
        self.ri.print('*Recheck a request (Use "ctrl + c" to cancel.): ', style='bold')
        while True:
            self.ri.print(' -Request ID:  ', end='')
            inp = input().strip()
            if inp != '':
                recheck_request_id = inp
                break
            else:
                self.ri.print(' *Please enter a valid ID (Use "ctrl + c" to cancel.)', style="red bold")
        

        recheck_request = await AsyncDatabaseManager().get_recheck_request_with_id(recheck_request_id=recheck_request_id)                
        if not recheck_request:
            self.ri.print(f'No recheck request found with provided id ({recheck_request_id}). Press enter to continue.', style='red')
            input()
            return

        request_date_str = recheck_request.request_date.strftime("%m/%d/%Y, %H:%M:%S")
        checked_date_str = recheck_request.checked_date.strftime("%m/%d/%Y, %H:%M:%S") if recheck_request.checked_date else 'Not Checked Yet'
        self.ri.print(f"<UrlCheckRequest(id={recheck_request.id} ,url={recheck_request.url}, is_checked={recheck_request.is_checked}, new_result={recheck_request.new_is_valid}, request_date='{request_date_str}', checked_date='{checked_date_str}')>")
        
        while True:
            self.ri.print(' *Enter the recheck result (T: Valid, F: Unvalid): ', end='')
            inp = input().capitalize().strip()
            if inp == 'T':
                new_is_valid= True
                break
            elif inp == 'F':
                new_is_valid = False
                break
            else:
                self.ri.print(' *Please enter a valid character (Use "ctrl + c" to cancel.)', style="red bold")

        await AsyncDatabaseManager().update_recheck_request(recheck_request_id=recheck_request.id, new_is_valid=new_is_valid)
        self.ri.print('Updated (Press enter to continue): ', end='', style='green bold')
        input()

   
    async def start_rechecking_requests(self):
        all_recheck_requests = await AsyncDatabaseManager().get_recheck_requests(only_not_checked=True)
        for recheck_request in all_recheck_requests:
            request_date_str = recheck_request.request_date.strftime("%m/%d/%Y, %H:%M:%S")
            checked_date_str = recheck_request.checked_date.strftime("%m/%d/%Y, %H:%M:%S") if recheck_request.checked_date else 'Not Checked Yet'
            self.ri.print(f"<UrlCheckRequest(id={recheck_request.id} ,url={recheck_request.url}, is_checked={recheck_request.is_checked}, new_result={recheck_request.new_is_valid}, request_date='{request_date_str}', checked_date='{checked_date_str}')>")

            while True:
                self.ri.print(' \n*Enter the recheck result (T: Valid, F: Unvalid): ', end='')
                inp = input().capitalize().strip()
                if inp == 'T':
                    new_is_valid= True
                    break
                elif inp == 'F':
                    new_is_valid = False
                    break
                else:
                    self.ri.print(' *Please enter a valid character (Use "ctrl + c" to cancel.)', style="red bold")
            
            updated_recheck_request = await AsyncDatabaseManager().update_recheck_request(recheck_request_id=recheck_request.id, new_is_valid=new_is_valid)
            await send_recheck_request_response_to_user(recheck_request=updated_recheck_request)
            self.ri.print('Updated (Press enter to continue): ', end='', style='green bold')
            input()

        self.ri.print('All recheck request are checked! (Press enter to continue)', end='', style='green bold')
        input()
    