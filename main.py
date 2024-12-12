import requests
import random
import time
import webbrowser
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium import webdriver

from selenium.webdriver.common.by import By


# Get all urls of microslides from the EBM website
def get_links():                                       # 爬蟲：抓網頁上的東西 (for the url of slides)
    driver = webdriver.Chrome()
    driver.get('https://microteaching.ntu.edu.tw/Account/Login?ReturnUrl=%2F')
    time.sleep(5)       # 程式暫停五秒讓網頁打開

    # Use selenium to click '台大SSO 2.0登入'
    # Wait until the element is clickable
    wait = WebDriverWait(driver, 10)
    login_1 = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, '.btn.btn-primary.btn-lg')))
    login_1.click()
    agree = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, '.ssoBtn.btn.btn-info')))
    agree.click()

    # Send username and password to login
    username = driver.find_element(
        By.NAME, 'ctl00$ContentPlaceHolder1$UsernameTextBox')
    username.send_keys('你的帳號')
    password = driver.find_element(
        By.NAME, 'ctl00$ContentPlaceHolder1$PasswordTextBox')
    password.send_keys('你的密碼')
    driver.switch_to.default_content()
    login_2 = wait.until(EC.element_to_be_clickable(
        (By.NAME, 'ctl00$ContentPlaceHolder1$SubmitButton')))
    login_2.click()
    time.sleep(1)

    # Use selenium to click '開啟' for '病理學PA0001-PA0304'
    # CSS: 網頁端
    pathology_micro = driver.find_element(By.CSS_SELECTOR,
                                          'a[href="/EDUStudyList/DESURL/95ff58f3-3273-e611-80c0-c81f66dbd800"]')
    pathology_micro.click()

    # Switch web for driver to handle       （？？？？？？）
    # window_handles: Move to the windows section
    window_2 = driver.window_handles[1]
    driver.switch_to.window(window_2)           # open the assigned window
    time.sleep(6)

    # Use bs4 to parse microslide urls
    # bs4: another package to 爬蟲
    # 取得 url of slides
    slide_lib = []
    for i in range(16):
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        main_tab = soup.find(
            "table", class_="table table-hover dataTable no-footer").find_all("a", href=True)

        for i in range(len(main_tab)):
            main_tab[i] = main_tab[i].get('href')
        slide_lib.extend(main_tab)
        time.sleep(2)
        next_button = driver.find_element(By.LINK_TEXT, 'Next')
        next_button.click()
    # 排版取得
    for i in slide_lib:
        print(i)
    return slide_lib


# Randomly open desired microslides urls from a dictionary (for multiple_choice)
def open_slides(slide_lib, cases):

    # 檢查有無超過304 超過就被刪掉
    key_list = list(cases.keys())       # PA0011...
    for i in range(len(key_list)):
        # PA0314 would be deleted, for example.
        if int(key_list[i][-3:]) > 304:
            print(key_list[i], 'is not in the system!')
            del cases[key_list[i]]

    # randomly choose a key we just withdrawed from cases
    random_slide = random.choice(list(cases.keys()))
    # for test: (Or we might not know the answer)(it would print like PA0001)
    print(random_slide)

    for i in range(len(slide_lib)):
        # slide's 網址(url)取出
        # 取PAXXX的最後三個字母 編號100->第99個
        random_slide_url = slide_lib[int(random_slide[-3:]) - 1]

    # 開網址，並用try-expect確認在NTU VPN裡面，確保可以執行
    try:                    # 如果出錯，則跑expect
        response = requests.get(random_slide_url)   # response????????？？？
        webbrowser.open(random_slide_url)
    # NTU vpn is required to open microslides
    except:
        print('NTU vpn is required to open microslides, please check vpn connection')

    return random_slide     # 誰調用此函數就會獲得此回傳值


def choose_mode():
    print("Please select mode\n1. Multiple choice questions\n2. Fill in the blanks\n3. quit")
    while True:
        mode_input = input().lower()
        if mode_input == "1":
            return 1
        elif mode_input == "2":
            return 2
        elif mode_input == "3":
            return 3
        else:
            print("invalid input")


# The three folowing are for multiple_choice and fill_blank
def generate_choices(question_bank, answer):
    correct = answer
    question_bank_list = list(question_bank)
    wrong = random.sample(
        [q for q in question_bank_list if q != correct], 3)  # 隨機挑三個錯誤選項
    choices = wrong + [correct]     # ????? [correct]
    random.shuffle(choices)     # 重新排列
    return choices              # 回傳四個選項


def print_multiple_choice_question(question_type, choices):
    print(f"{question_type}?")
    for i in range(len(choices)):
        print(f"{i+1}.{choices[i]}")


def get_valid_input():
    while True:
        try:
            user_input = int(input())
            if 1 <= user_input <= 4:
                return user_input
            else:
                print("Please input an interger between 1 and 4.")
        except ValueError:
            print("Invalid input.please input an interger between 1 and 4.")
# The three above are for multiple_choice and fill_bank


def multiple_choice(slides, cases):
    # Prepare question banks of both diagnosis and organs
    all_diagnosis = set()               #
    all_organs = set()                  # None 避免出現重複選項
    for case_id, details in cases.items():
        # list: append, set 按照字典排序，不會像append一樣加到最後面，要改用add
        all_diagnosis.add(details['diagnosis'])
        all_organs.add(details['organ'])
    remaining_slides = len(cases)               # 現在還剩下多少沒用過的: 一開始就是cases的總長度
    # print(all_diagnosis)                  # for test
    while remaining_slides > 0:

        # Ask which diagnosis is this
        # serial_number: 玻片序號。執行此行會開此序號的網址以及取得此序號
        serial_number = open_slides(slides, cases)
        diag_answer = cases[serial_number]['diagnosis']
        choices = generate_choices(all_diagnosis, diag_answer)
        print_multiple_choice_question("diagnosis", choices)
        diag_input = get_valid_input()
        if choices[diag_input-1] == diag_answer:
            print("Correct")
        else:
            print(f"Incorrect. This is {diag_answer}.")

        # Ask which organ is this
        organ_answer = cases[serial_number]['organ']
        choices = generate_choices(all_organs, organ_answer)
        print_multiple_choice_question("organ", choices)
        organ_input = get_valid_input()
        if choices[organ_input - 1] == organ_answer:
            print("Correct")
        else:
            print(f"Incorrect. This is {organ_answer}.")
        del cases[serial_number]

        # Ask continue or not
        print("Press enter to continue or input e to end.")
        input_value = input().lower()
        if input_value == "e":
            return


def fill_blank(slides, cases):      # Check if the input == Answer
    remaining_slides = len(cases)
    while remaining_slides > 0:
        serial_number = open_slides(slides, cases)
        print("Diagnosis?")
        diag_input = input().lower()
        case_ans = cases[serial_number]['diagnosis'].lower()
        if diag_input == case_ans:
            print("Correct. \nWhich organ is this?")

        else:
            print("Try again")
            diag_input = input().lower()
            case_ans = cases[serial_number]['diagnosis'].lower()
            if diag_input == case_ans:
                print("Correct! \nWhich organ is this?")

            else:
                print(
                    f"Still incorrect. This is {cases[serial_number]['diagnosis']}.")
                print("Which organ is this?")

        organ_input = input().lower()

        if organ_input == cases[serial_number]['organ']:
            print("Correct!")
        else:
            print("Try again")
            organ_input = input().lower()

            if organ_input == cases[serial_number]['organ']:
                print("Correct!")

            else:
                print(
                    f"Still incorrect. This is {cases[serial_number]['organ']}.")
        del cases[serial_number]
        print("Press enter to continue or input e to end.")
        input_value = input().lower()
        if input_value == "e":
            return


# Main body
def main(slides, cases):
    print('press enter to start')

    input_value = input().lower()
    if input_value == "":           # type nothing = press enter
        mode = choose_mode()
        if mode == 1:
            multiple_choice(slides, cases)
        elif mode == 2:
            fill_blank(slides, cases)
        elif mode == 3:
            return

    elif input_value == "e":
        print("Ended. Run this cell again to redo.")
        return

    else:
        print("please press enter to proceed or enter e to end.")
        main(slides, cases)


# Microslide urls scratched, 304 in total
slides = [
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=FV32RG%2bbW1aBSHShETWQybOqEiCc%2fgRAZ3HrvBx317SV%2fzWnLwNj5SQhbeAYbhX6jWDD9c26gQlvuliLLeGjoIOI%2fmuNRhRjAzjUwiHyJRM9GZ1bpO8veST30Ml56qtw5%2ftd4YLETuU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=DqwYbc%2fLDBJ6ylbprf45xJN8zsc73069T0HDgTnBT%2bRz6QRt2h8SJsWzEbXW4rKEuTFznyiY7zDY4yQTay7WxZ8ES4j%2bolAw9macKuac3fyZcU9puPWsecuNliVLSky2zs%2bVq%2fkBB5Q%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=KPQwbmMHvAOe%2f%2fXAygFkSQ8RRLyMAD1NgdsRDhHr3ZyTRqmQyeNmngaAuV%2bPrbEAdlIDWlyZoMdwc9p9vgoXrVNYvbiqRcD13lrV60Gf%2bko7XbgNgB62qx4RVVH2YtnjBHuhlJIA2Ho%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=X%2bfb9h%2fqeYQydlLc4pqXSmuB7LyWhuIWDkwCzTzBntsuwpvU8KsIj%2bVfODPEHtIVn6gRBef7XRWUVcXKddWsnGI0rTGYODPwPnWRpAHI99RUl9htlUmoVLrYSSu3p4uD19jDYSE9K0I%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=LNpvqBLFym5dVC2i2XWs9L80jXwGxjnxShy9BGJrtK7Cxe5uMWt4pxZPwCHPlZKrBfwdNN%2bwIgY53wbHn9O8wtm5nvZaC8RL5IKGlr52pvImi1%2flnlXKetsPGzGZNVn51C5U5EGlGDo%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=3Zkv0i5QHscJ1HQBXQpP3xtnpRxylU60bCO2wO%2fBcrapuL3S%2fJ1ZLrmzLdouYdegJE5rTvbIByY0sBV2nA5IyN5MgVHbZ4GBbTcmyOcYh6Tv%2bpDPRPlnODYcrlGdjYK9IjRMjV%2fCfjY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=EqJEclrAIXF%2ffbm2KAaMhWZstmmSFljyIIrxwv0iv2OzKlK%2blbjZCAN7qIissnsBV%2fV%2fvBqAwBI7cucNi2lfcT8nHdi7ErRt0ucAFBywajEiI6PEGwQ5IuQT3IEiwWQhR5MeiD2zoKA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=5iXt5shxWUa1yCbcnBkqnKmXbv0tn%2bJvzbr7HWsU7tdG4VD4E7cYEv4A7u5P2ypBmggu%2ff9EZhvhkHf1oDzCpdA%2fByTdgWPbx9yAw57t4o%2b1%2bVx5wyqlgt5nJIU5QiNOC6AJ%2fJJbKHs%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=q0aNy%2bZkbSL3kVzf0GLoVWEtHCKxU8p2Y%2fcVKe7SelEhIFWxT0yIpv9keDzir49vkQd%2bVksI2PHfbCb%2bbcQqCaJb7oYI%2fLcA9lLMre3nYjBFskgJ6S90qRoXU41O%2bURR9Gu3oVSpMTg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=32z5BKaUZ02qllnQ8AfncTrm1Kuz%2bIaqqg0NbiqS%2fz8Sp8TbvTRLW8LPW2lHP1ZHtsFO%2fbqKyO3gt7Pkb%2b4aEe0d774lOROX%2fUdj%2b0tYCKcBCWu%2fqSQwy%2fqJrJu%2fRd5VGaBfAVmOdAY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=QB63fsmyxBdSMGmA5pxkgcqp%2fNOXRK4wdNTVO4DU1OghVk8nK6SOHSAUo7T4smcYTZUvusSCD1ARRWCM3aA92Kz99%2fbSkXCk%2bCrYVAO25B5irL05S9c8rgcHq5EZ4w0n9uTaRHVW85U%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=KDek9W2DMlbGym5san6tcK8cpcJUPPLVJAKO9Rvnph8o6doEDcIZgyqgljPX1pLdgKnG20vsnhCD%2fr3zbKgR2D2FGHDAw7DiXp8EJnkhDL8QLKuCxHnZcimYM%2fh8cZ65eJsx90MUye0%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=qSAaGLN%2bBScq2WizMtsRaomS%2fqsp9ikoqXanCHrJ9NgJGaRJvO%2fW7Qmv0zUDJeksCSY7DRbnnZwkrCBw8E%2fgcekUMboEM95JBuCOLorOe%2f0%2b9frhBIodJwDIYRljxv8KKZM7iOyGsH8%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=6z6bcrbgtTFhb4Y08QZX%2fAPbPiTHs86ESOLTm1D5%2bhBEXgzPrCteABjBsKABX%2foKFdWMvq%2fQhHgNFlftH4Ec6rf%2f4Bihs%2byt6GDEJr%2bUTsLZpjVVVKzFAEtDRAtSfWGSo%2b3AKHuXNcY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=aC6gcuNEYWk4I8WWR29TjZNTHID7fLLDs7TWXZe%2bjBTm2pT4CG%2b7RPv73iw3BHQzk9p%2f9cRLV4QP%2fzk1Mwuv2jFApHJqL%2fRtP5WOn0JkIVj800xq%2bwVm58aqdFtK9b2naSI6QEYe5BI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=8ykfvRALTuWsfviFrxkJPJJH6Y4KDJxKfVB3fTU7XrxFw7cTZCo3berzajntERoRa8f2CdFEzoaR7G5TXjrwNeI4PVpSlMLVmDJjBguA5tYFW5xxK%2fy%2fz5C7B6FuTQjQNX544ckodjg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=aHsKfBbIp5jh9ujnqjg2DiFFTJHZRzK73lNz%2bJbG8pUUc8yTj0gDx1HraYiPqkL11y%2f%2fl2UrtqrBKMNyghNK0nvyytoJ1WQW61R99mdDKyf659VLgH2ZCyLMqKf6Ncq9e9Cv6g6NduA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=ndCIU1bVIvZc0KNtUoRjzOQB48JN4S2EmMnhZYNv9ULUCcbXLGAus7l6ssjn68%2bYycOSzy3mawIt8aivgVdGQfQm6SCjagF%2fy5mNb3W1EcYgAHOrN4t%2bB5hdaSPbLITMcoVrqWxTsgI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=NUb%2fOfQw0KqfWDJzmAHsujXLXZH%2fInqhv6QwYGPHSZX6H%2bErnG4pqn0mxf63DUbYD0BEa7%2b4CWLqy9xvYqHmb1PhSycpMp%2f9mWMSzesC9yzzTpvH%2bzLRn3yioyj%2fVGVwFvMoJedstLw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=l34rPjKfp4Hqe2GQynGCJ0M9%2bv3tYD79xEN2oKWzUsUY%2btjvn%2brd8L0RZfhObSOqu22x5ME3wLxmUr%2bZ1fPq%2bQ8tKksD37BTy4gtY1La%2bVwDoXRgD8nVR1IcXBPTABDxazYn3Xy%2bkEg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=AT4H7PfZcz%2fTimvWML91cJb0eMJ3C0XIAWFYNj8wU8pNcsdcnyZsySG8W7%2bek7EdBD661MwwNKR%2bCsxqi%2biVaHwHCZPZgEsYnyP8DXOqtMNkzSVb15UaBv1qMXTDmjRYW76IyZG0ipA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=c18%2ftY35LxkFdt0pLFcquhFi3dpEbN7gQet5%2f35Ihcwrsrtr1IuXQv1Z%2fRzr9sH%2bI%2bHcUeVWkvHbuRsGxFn0UA6syL6b3SHJj1dnavZyfh6PVZlOnXxKUlkYw2sQGqeHZqk7TRdZ3Y0%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=lAosEm4suZMSINOXvTqDOq8VgbB6jNq%2bs5YmUWhbAF5ZcBSaHqUlssTf1Cku9jc0XQ7Q4hGFHLjxcTM3aUsJTiST2bo3mA%2b9USvIWxTtk25CyVLr3Rw%2bKUPjDjcE9L%2f7MEsUtol1zWA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=iIdQdPfyG1qRa4ET3X9XbMmC7UGpVgRhV%2bsP%2fGPe95R8psjShcLqi0HaI57J8u2Jtdsuz7XZEZsOrq%2bcg7hrOQ8EJZlqD4W2NTYfteADNfGs2eeis4mHO6bg69uCZPjF3LYx%2f34ZaiE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=RvZgLBYlZ2CzCN9AWHsP2NTOiwb8A2poK8Xqdw4h4CF6gknmn2EVs6fe6QypgtaNw3oV1Ic3yX03ZhO6Um2dG0VXMPQ%2fOWwaeQmxFmszoYFi1KHMDRCH4UlXlP8MXfEj7q%2bMQvEYLeY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=PmZhxNxjmLGJE0C8L8DGxd06uM4q6Xm85tEEBncEiQakhA%2bk2%2bk18hy6N8sOx4ypTHk4znn9Agt5bgoRUC7IYODBXBPDAkSf7yK%2bFJ%2b94Ts6tVhnRLiDwiix3ZtXbPt39MBUa3Dxu3I%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=dgSsM%2fACxsF4YCLoFsc8BKLEvKK1%2bDol5UcMtssrd0dwAcAuQ0g52askHZJ93O2gR%2b2k%2fADbwBBJJKnAVxYKsCyMqlECmJXmRUbe9llb23rNKL0yCwbXkAfFg06x9KAcvDQIG%2bZdk14%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=FElsOhRUB9KTfTnW0Eo0vY0sFgccCOBbHiwMFFj4Jt1GCECmVNw2CGmvYJmkjlq%2fzeiHZVz4gbJJui02bn0lIHx5qZxLJqKyhKO26SzmCggoSbwSrEkudnzrRjKMKCoR53FduEmDLrg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=SYE77SFmdJdEdSL99BktYjYz28ZCJM%2f65hC%2fc%2fZV6C6Y4egzcutqgfXhg1eu0fGZoBfvdT0rcAaEIxVKW%2fMjpfYH%2fxsX31Hd8Tycm0BZt6k4OuO4MeOji67kYriPhAdSHXsStILuSTo%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=4IqXFh83jbEDmabt1psRAD6VJsHZZuUCd6gPR4iwxWRCTswhzx7YKsOws06eox6JGcYxm2lNt83CNiPR%2bK%2boipafG%2bCm0ljK20%2fjWa9S%2fAB8a0jLSJ2Yc%2fBiG9mGoaZXInec37ynm%2bU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=QeoiT4SFTbT2urW7gMSM6Sg2STReQMcXkRqVIMm%2fRqhIJq2Vamkq%2fpVPsWPyBgLIDxAQ12tzBJEt6cliWcwojgK9AshA8OEJAtwDywEWXAlnTts%2bgLgIOwZUZi9Udldp9zJcfDDRSUE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=zdmiAJqBMYs%2b7owfq6w2y2gxY7PNaiO0RvPzaO97cI2YOCIIRqDr984k0yuWuiGBGpguprCdCBgYItR%2fUIYHjbI%2b6Qm%2ft3AjCCUFGOSC7GR5ovBMycc%2fFAcylgkSsHQv9dfSiyjEE4w%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=3LKlXD3p%2fshPVNc0HYTAdqjXB7SPdqZD5v9Kup%2f70ISe7H%2f2vNJosjsq4a5h7Pha5EqlRLxi5sfEEmK5ahF6v%2fhYV2d1t9hzeH5u%2bDqw%2f00gTfaIs%2bq8GRpMsBm67Rn6l%2f%2bU5SgXGNI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Xqn7MS3rmCz5DBlclL0WWrQmO52nTwVCES4AnOR0cD5q37mx6iPX1IWlm47f8cOoqEYNWAFrvaLUZe6q4B5gcedi8GPElAOi56Zj4B2ZuGhbuBE%2bGVX9dT6%2f3L5KtfpqBOwFZrMB1Lg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=jgfVI%2fXKlPsA4H9YZYTe2Lb43kA7JeKD7RsPZZ%2bw4rmLofBUh1Lcd9anexptN1oNtQyBzvPPotpwRi1vJlEElg7gbO2T392QggAKMFXc6fLGjGPP2JZ72x9F%2bKskxctiJLSrKZkG5Oo%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=jHBPw%2bgNpZu7kcd9Q%2fexRhE%2bXPH5O3mtbvkocarfNBQON8cO4NwrsgKMvrJpo0PXX0Lsbr%2bUgg7TdBCor7ZsjRf28wF7CPtd97Kyas73B%2b3pqtpT3goEHm1rif5AqwS5j8E0IM%2fePuI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=VGZkpcjb92aGzSHCMVR3%2bd1zIITQQMnKMYIjiP9qnT14CpUUPuGRq4vyZ2UDeEp0rPTi98EDKAeLkhUZUdTaL35MqJ5pBnDWuRORMmO6J%2b7NjR6I0k%2fWJJCHpiA7AcoWxnxzTasxync%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=VQVfkoGRX%2fEoJE4Si4ozHkkjRuVQp41V%2bFWSJD8a0DrbpoFWPxFAg6gcZ8AvevEDDgX7xcC4kD6%2brHqvFXnZxEssgvfhl4bo842vixxZBvPrS%2bT6VjiWSPtu7Jn0KcfwEWwg8VgEGBQ%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=7VJ9zEqGDPXPtz8MQyxLaWQQfVPVuUgqO1VH1zOIcSA0mthE7G7c%2fCio5Fy56TPJyhf5FWR3rLxFzvlImqlhuelZYXjjc9Fkpm5enPWVf3zRe7s3ko8m05VRul%2fQAzbIifNLwp1mzow%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=7JJ5cCmCloRzO0VXEJ5J23udtwC0R7%2fmC1pMnNsnPqXlnVCk4BDtz80eQwmVH6xX0hK1Vz%2b4OJkaE7kcVNWgUQiUakZCb3ddun6MfIIz2mKdNnhLuxvA7J1vRy9eRbqxjYg%2fsZtpisY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=JH3oyVpN8eRaJ0CAeoIjcCynB4f8lWn1VfnzVmdjOVpbeq8Ivrxb6FEW5TGgoccwH2%2fKgObLjoiqiQ47zYHbfclf6MS%2fmlYbubVvKD5B%2bbz3b3fi5kD5bO29j8XSVX1seQ8v7KliLRg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=je4Ijr1RVR1yYwRqxcFVEkTc0%2fPci48DcnqALxkGlniiKA1fxRcwonN9dznqn39DMer9J%2f%2fPtqdmxGsfYJPH7EZEV0Amg%2bgHSbDqr07S39CJOqOlKoUhMl3TO19dhJAQS6KpN%2fj0coE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=eiPpsiAzUKipvOlm%2bUVDywWBUJ0uh0h9uZrKRNCVoOyyO0gMGzKH2BJjOI1eNlz47L6xKwQTtx%2fHPiFehfKeKH8GxultyG9qsf%2bZ2POKXMXOYgNgmOM3e47HMhadTADdxVnkitLoGHI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=hlDVCjyAtOnGDu3eihBuFNEPcK4LPOm8mOULttLhR2WSWe6eYjid5cg4P0AwD4nHbvea2n0ABm8KXdcptUsx8vX25JqLIdNb6A8%2bV3RHyCKBzqfonoJuX4bCTmMQmc2qg%2bTw6mDU2go%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=g8KYoHAqX5Lg2nPZarEMlzVsdVI%2bL9Z%2foOEdjZ%2bHK00SQfw9pHfbWTxs80dvKrFGkDppx8n2R3vVU%2bARgSLYxGgQJvAB5pHklwlt%2b4R7C1QNKMqY9VxaM7mZ83sP%2bKDoHoSepepHeP4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=fVrlTQAm7dXBS0Xyysebl8W1RquosirOG62Pot14bGunZadtWWwIYwVSN36DuKmOfTeLZCZXImiTDYB3AnZHruSbCtl9n5Gkq3mSM5BcUwZfA5F8x8dGHhCMpFy4PU6g7KQOMcSa%2fqE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=FQ%2bUuyQrLGxUHN6QuioNP3yBlnzNraGfh6Zon7gGAFTkiVJpPWn4e3pi%2fLt4fpFvadY3Z4QgawC5%2bZWd7fUwlMWrLY9cdGF42VRhz1AV%2brA4xCVu9d2eDV7q3Z%2bzh4syYzNxLprqqR8%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=4A%2bKfgFEfzjrkAreQbvuxQLHKxG6W6sq3xNmvmFVwfoDmnw%2f%2fLSyvBvwtCEXhjKTyQLCu67iLCq77zqCCtGwAJB2TlvWdPWS1REhJP4nrnWC5mmjdvgn0oEYaSMoBJDs8oAcI0cerNM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=li6bMZ4%2fEFnIn5P5CPBZ6%2fRuzmBTQ3rAvRN6s2onGc0UBgg4N2jAN5vJbf8FHkNwJQU5O2JQEOpEQigzsY3lp9W2m%2be1rd2dKDNgeEi4mO%2bYppvABmIFvQ7lI7lU8OvX6C5hvO50FbU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=tNj8RJiBu9%2fyoXxi3oV8VCSIu2rqAZBiVjZn%2bhpw%2fd50vTj%2f1Xus31EyB0wDFV6rtnApDBd0aBNPWpch4yhJFt4huY7YLEa7JDXMtSgZZ%2bNQtwreqHxspC1J%2b9%2fUsKZd1UbIjXJOHrQ%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=CfyBSdUwOCzoXOTATUbdxp%2f%2fu2gT9t19yKwTcCMVe9RMrQTLQV4Qtu5bFilJO91urAuGyXoG9LylGo0cI%2fCrwr5c3MGmPqvXdprnYIo4Jv4duwKiSjCL6h4bX74%2bG9YAMBb%2fxMIbNZ4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=lLx166UKzS1hn4puqGz3Gb7UWqsb3EmLDu4YB9wC7FlwkK%2bma2HG121IUtWKQq%2bD6v5%2bqIOgn2r9kqhL5bE5V8zFDpTI%2b17V1nIwNrA1%2faL88FGDPaQKYcRRQcbqAdVceB3nsfYCucM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=AKoocQQcwbxY%2bf5fOsT%2bJt5fs6BYS1HSSdu3XzwqjjttjkZ3TtHHDTg06OlELKl7c3%2fDXlf6%2bdVAU1WvvtIGF2MTRSWi7hehN%2byYY9VIbVsG5herghHvBdpgbwVj6WJWhXvyqSCd9VA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=ZJtBoY%2byoszWe5GkHPl6wT8i9qw0WajQCAkeeKVXuQrnmsmcsnbqphJ%2bDwtsZd8GN%2bjmni0BbOLyC4MhvvvKC4XutPn2Yy2y6HVfvv2acwzM%2bRap7eo6urp0tNPu1jcxYy1o9BBO5tw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=jad%2fem3SkSY6GFpRossGwJiX7QV9qO17w1OXQZMUdd07v%2blijpppe%2flvvPzaWFbh4HWwpvOXleQ%2f49rmIoH5qoDcrhK7OcLFRLHkvuLY8SUq%2bT88aS5WgZE9RLISmlaQDeXtfZ%2b4Yh8%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=hhWnUktDL4Dm2dpCn8mtZVo%2fTT35QrdIKrFMjBcbKGwvO6Yjl1Dim2eFt0p5QOUnr3r5ASXb2FgRvetjIPQ3IqeUEAl4FpayuFRWpDrhsy1JUKH04svT3B2HutmcqrHHfZRR3J1Yiek%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=hyohuQT75PB4GRb4URf%2bqjFzUHhiaFSbQHhijPzYj2sru6v0JBrz%2f9HLQ1JH4VvqDIuTLXnMnruUV%2biNrJJKvSwqyw1IoRZ4RrRe7TMF8Z%2bZI3dLjp%2bLtkxFI3V6NQuuUligKscebSE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=a3rfM1LRlCzi3TbdOrxFrovVPjeGJXwH%2bAxM8DQ0g5rPoHoCL2AeFC0NpSApqE8P4CzqQBoyLoo4STufOLipA84%2f6uH1YTN3fO3EmcW2M6t0YrufWQSrKKSe5RVllC3CPhde5%2baIz%2fc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=3AVvVlP7hS9ILFjObz31GE3KPxoHc%2f4%2bzjEyFAI%2fIWyLIFL7oPted0J5RuUf6QXkrC9OUQDV8Oz01x5va2pz%2fLELtvk6UzY25TdQWI%2fDh251NlQYVweEx%2b6LecWSAwcrUvSz3hpMCAY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=KaI8Z%2fzQw%2bVCJREK%2bc1h29nrm%2fQGrwPgHBfb1Ul72HndTQz3hwb3XqBlQ4jCLwr8svaI7nXdu6SqcvU6Z5SKmrAiPCMoVcA8WTK00v2RSM0N8N1M%2fP1njH4UZCKyhKDsA0yD4uNMW5k%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=EHBQILI9Y90b%2fRPx0QAX3D1KupOzE21bVm8W2pAyRyGht3FD%2bVgRBcpsqP7b6GsMjiWM%2baDkmBLfHsoqNOgfMGVoVi986rkP95oHrNm%2fXw5D62P2bsLQjsQBHIs3Q6bK6JGOH7s6%2beA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=pZlViyvxNTWktvrlIdeAvtnIiP5FXiVGif6xpWsHSqkkc0nGFoHgCZZXiMl4ONacScfNyAPsKBX3B1WGs6VEcnPCFJ12IkUmoMVGCGzDUQr4%2fgCyTGJ8IHpzxEK%2bGnmU05KBLmq%2faqk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=z0Ig6DAcM2qvwTcEuyigwafzykDhtL9Bz5%2fM%2fXsQMeGdIJpw0tE4ZDbDLks6KLZ1hUEVzpi20fBrS%2fyuEaoZVwEYeQ%2baoQmhKXmsZIKmI2NKGFRBHgrx0MTNYWLKjIoL7slykH7UYVI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=9FWXK4O0hgBtUTLsEb9ItaLhXQSNqcr%2bkHMkXBmX2gIzctKdDPJ0tDlyqMSdBpF1Rf4iSqPgvKldMAe%2b%2bvfKJGfeZ3mY%2b48V40wZ7hsgoTXnZ07BxWphWgLEsazCSyW3RUyv35QJMBs%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=bso0VM3PhfmnNDXN4ILHE3XVgNFbD5JpPGXUIpKBlF%2bjMiJM0TLFW8l4mrYhN3NFIrfZCpVBmGA5w3UArBlLLbZqRWZnz0DxaIHH1QsHABUdDPrONFAHyOMAY6Q5Tu3le0tICKMDV74%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=bKc3U6SVG1BGy0TqJh7kXdHdnwqpeiFYwFQqmAwS8PbnT0WuMZerbjKcL5LAKyR4uiR8k%2fX34AC8xgahf1ZE1Jg5J5Lrb0yU9OWNw6san%2bwUShw0S7P2Nh3YS7lyTdjfm6Mwr%2bT4q%2fw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=CTa1ojxN1u%2bUvrlBbUPqKFyCUgM8IGkFJ7UbZHZ8q5X2EXQ%2fYQe6pqLMSyaVcQCKrn1XH%2fZwnHatGID5Aixh8aw7AOcpi5FlbWMPcR%2bNMQPgRcAk5oR808yKkEGe6t82XGvXuNWALnY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=cGk7Y86neF4MGNjvJX1im3LTGysoFdcEG%2fUjhsIyfBz3WrkWehfKpai1yoBkT8D8%2bfyV5PNNop8xF9BNleDiiBiIbni4M7m6zG1olLEWoVrWSzC6vOkaNzjY3cKp9q3Fh7Efgg4AF%2b8%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=c9EodwK2XGYbTuxK%2ffr90rTZ2x9U3B6No5QxqDNwS2fEdWWduzyL0aF4bYYPEjHCnNCb7Xhgh%2fLB3cCmUlZhziwA2FtkiQZUy3NMmWoq%2fEkU3SzV4zzfaKdqzwAD6msPWt1p2oCSybE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=YwJEd6uhE8HyUOQYsqOg%2fKtu60K9vgu%2fgfgIZc4BPn%2f%2b%2fnGwuliMt2OEVoR2cVSJq0FLX3PwyvmjhHjml6QHeouPf6LDziSaxUUnAaZBCrMcFcImt4j3Uh4yjJpa25jUmBzf8%2f0Sgto%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=B4oan3yW1ro%2bQCnf6PgkvjsAsd3XdxfRVGNOI%2fUnzSFkC1%2fBAqdgwxdEnDkGhNSwMVHIxDG%2bW8VQeJsb4C%2bwtimark1fd8L7E%2f%2bmZjWgC9NiOSfHhmEpnT4DUW6NSl%2bN4l%2btqWFbiWU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=ZUq7sixCawBba5VKtEvS0mO4NjV9cwrqEaZt%2ffJgxzmnBaR%2b7NXvIUZ46DQaWO4tXQ6vgMvJlvkqoa2hvggoYWOE5BpVUTfbRENKuJyYk09rOan47emtTqPB0pNPgziozJDDZ40vbHU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=D2heR5AwTCD2N5X8dvez3YM%2fErlaIZs6gJxaiycY3Qpf5LXNB5nXfiLO03MZMTtjeG%2fS%2bYKW%2fB3mwtlmr0fS9JUkXgrP7ADivS7nGo15KKGpWO6DgVv8cavrTVMdxMD%2baL4B2w49A5Q%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=0SQv%2fD3fVYraCorH1ii5UyjZ1SVZ4xYWkX2ABBR73E6av2wRozYhcrHq%2fN6FhCiv2KImv5PxeZHo5dghjo0bIfImJJkstcWTItFo5cp7cQ7E6NgbRJ0M7gtayVnz8XkWIQ5S24jv%2fkw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=jnoMXkK9QTSXkAYH15kDqarf%2f%2bIvWMjLDEsjSKajWFxGZlCbfHGCZIn1EjLo3wn8ksylPo3Dmc9rTXvUKfUn32RMcykCNG5ZWvwsZwDbUKnrginqt9yX6OiUl88CCx0Wto8CSCRrjM4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=SG5nFpMvlYpuiLIQeh0%2bc6qzIuCyIgBvktgFyjWLJUKrnv%2fVjARQHt4JsXM7GbjpMTr%2fUi5laZdR%2fO43qDCzKugGr5TfNnk1fWuPHx4P5bqj7PWPE%2b%2bloqDFN%2bZIpooQLn%2fG%2fP5ml%2bw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=GtCRTnWRsd7UWCpuwG8cmR5NNBG3N21LnlGFts6%2bCmzcM%2fxo8dL5%2bSPY69CSwVjMhhkE1iber%2bn2JE6uojCmH2OijHvKJOB8C5l2Ni0Mi93FGd9TPWhDtcZ7F2CkrlqypN7aTfhJMi4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=qR2sIRPZVOI85edzJqIRvVYx0%2bhhWcXAOQdowSf8qqZnLuu0V%2b9O2rxajanycbee3OKlP1qzBPMu8dZtDLRLdLxwZ1qBXyQqjH6b4P0aOQ%2fAffZYRS8TjcOnthIcRjLYhdiEAH0i1NA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=xHNn39%2bELkPQnu8jXUj%2f160rQhE9IunAH%2fbIpnR48Y8KnJ71%2f09E7NfKjWjrzCVDoPpqb%2fbrMzJYvto%2bdEGJFzNHixXeCQzEaIZ%2bQ2%2f4gmXr3QG2x31gb6MSxvsHN6zNu5xmcWJdTsY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=%2fCR%2b2OMGj1Tx8LaCE%2b9YVgBPcjyuVvjHnq9295BrwCrwCOJuPePr3g%2bO9FbTvpCC1BuM6hQFwBMMowSx0TkF7N1mlR3xZsP6xOiHDKsTwIEZ0xqulTV%2bArM0KWFlWCnCmbqaHvObWG4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=S74CxEJH32DfnGZz9gHW9EaZLu8UAuo5TsrEzcg53gD9WVod6P1%2bdrBCIcAPWRcEUGdNF06BVCcCUgh9rkQLlM7uLgljKzLL5W0e2poD4hrZZ7waXaL9GqtawkcxGLRi57vBg2ZkQcc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=DVFwe3GihjkiLRGHMiyaQ3ZZN9YdSTv%2fHvKGLV0VF1t%2fbUpHlSHTt2xtk%2blhIsWHxLy6qIw4rAnNe8GiaVkkcnNTl%2b58EcLtOWiOA6%2bNv7V%2fn8U0SDMkwLiLNWZh0JmYzdKNTAvwfaE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=T3yZCN%2fuyaMTtil2Joc7JZunnFoAeyOwra6ZH3e5Ol1WVMDgPuzDTcT6NIr7t7wjELtNkD9R%2fRYSVPV8cIEoS9fQ8AIfkITuqgKy7LddNMkOCyUsqXq4BF%2bTDJBM7i1aSzeC3NVW7J0%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=DDg5dmrHZO%2bmsbHGiLkqsZaOb0UByBOf3rx%2bCov2mPoC63F%2fin%2fB5Hce2RScPGhjah74MCmodw%2f%2bpTaFJ4%2fksNwD2OKugHasGF0hHmqGiHSis1xroi0FQjwp8%2fXt1bNqraJy6q%2bJLd8%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=EnKJH%2bGXk4mBdde5l0CxWUt7SO7j2D2Z%2fFJEnmOcDoFE4vbRhGdYif5XgupXl1tavsLAAZ9nI4cs8FH5GuK3KJH3oV7Qbl4y0Gqy5QkerJAzIKvwn2RFdTdbPtq1Z5Mzh5X9iG7d3X4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=TWlsOQ2%2bTz%2fsXXJ8Wzre%2bIn%2bd1aJE%2fdl2bHDGp3FQ0QusCFYYsCSSbPPzV0X6ZQXR3nplAhu7HD%2bwMYDXszXD3LfUooLge7taSJFY71EsQj6F2F3TuPPtDJWU4lQJIIKXEtWLw3PewA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=q9IIbTaV1w8M%2f3lp57VJQmRrBcM7%2bKffG2IjkszcAWtdDvk0zMaabnSK12DF8IvzNvfuHlGCtoPHbKuAg4Tys81OOfQO6bZ0sTPiN%2fIIjmz%2bfry%2bNYpnjHF9gS561FHZvzw1Tstb0L8%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Dqy2EPpxU7q25JQDuQO6vcbBfUF5wjrJ46lat7QyMn4ylPzfYWwbEfp8OEshFhVHFtDA9GfGf4u86zH%2fErL56H1MqWFBoqXE8W9A1XjVwM6oHBwxX0dQyW6rPkQNfvz%2fIhGOBKKI7qM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=N4%2fZxgPoTLvJF01OpPFZ04sp3WlYckohw615peuDdzSsP5%2b3OAIxjkCH3GlXpmKJSVAtGZnleECtbXaa8p3x1%2beOka3rhZhHrTh8Xq6cXIYjfOWbWJokgPNAUivyXx%2br2bbx8TV%2f5Zo%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=KkflP%2feXRwcPbv%2fRX5ZPmDDbkqH8UC5DczRvLdhI%2brZQ216rEKsJqH0TfZKueSs7XFTaYgGRFi4GA5Ibdkm0QWfjg%2f9VxzfGaVtpn6knLi7u57Cepoee%2bH5xZ0p%2bru%2bulXUkyYWd3z8%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=wVBJmqgN7x445lGkYvC6gWb98yxPiW%2fxLcKv%2ftKIg6stoWtv06Cyc0UYqIhdalpSQ8rcBIr%2fmQgAZzklrkzGcku2Ml5m061Z9L%2f0EHjRAvNoarFi1AvayaM1oF9gLosc492CfUjhZAE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=BdKDxoRNxwhsintUsijt3gVT6hkbmK%2bdGw%2f4njyOu7DMmrHYijmQxIwUL6zNlyrJhepGj9xINmWBUIUxX4oRs9xUINetnN%2fS38RJ%2byRhLvh%2bFkQXTEUpH52S2O1%2btObsg71D4vgc7jA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=RRa%2f6KKyA7VJzMyP33mp%2b5HSSebKMsgtYCOlsei1Ei1WYnn0cNvc%2fxU0eL%2fZvXY9bNQOEf1vPp2%2bJd84VtZEbq%2fsWMAsPIUvGvtx7u1m3IqiXbPiqN9QZ8tIUT0YJq8%2fXqg3x%2fw5yXM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=y2jQaxMLz8CEDVBfWjmvJ7wVDP3Y3Q%2bxmiVk6M1BbK4wD391%2fiRlEmjlrxYHLdNu1isIi0BymMhP94UaYnbPdxZ04Ds05WABoxHw27YK9TXZPpx5agZbLzrawCb4mK0xx37OgvGJ0Ms%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=87fujVNhNqWLTkEtfb2Q0ZH9p77MhQ19wWJI071%2bM%2b6IHMwioBejClcByUpox%2b1H1lg2%2f0v45yDIpYWgSv7F4pZq0JNd7wWJl%2blH2nUl7Q2WypZvGpLfRAENVlIg3fo%2f11Rd%2f%2fGLyHY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Hnq8jb7uu4t9AFD%2bzvotAx1ceJW45FfM8DTsDfj5Y0Ftmj2PqAmmh%2bJiZBo9hfPMrF8qjp1rq6A1BTOYWdLLJu2EZxi9suGswixQehrsXOVuklJT%2b4TWmP8xvTkMPMel%2fx3%2fgQYjOt4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=AAub7GHDTFp4ow9v8GN0FR9P3FkyeifhhcBzEHwWadkPChhIbjrcwoMU2pA4uP9V09vjM%2bsmZcXrFewFVigS%2fFWylVSsaG1zLsxzXcBmR%2fEQyB0BPJuSnbRu82ko31kjINVix6WCmxI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=ZvuJ8hnPGMSDS8lYwDYvr5lcYTe1Sw%2fvuxvwIIU8oFPFDAWFPUm5GxW9F1B8grE5Jl%2bZZ5zXQ1%2fsCl4p6LbtaHzRzkXXbY30s%2ftoL9n9UAj7WOYGnS83E%2brGAOqI6FmFNpQj8%2fTuDqk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=%2f%2baCJvR6vXL2%2fU5LaNMjrUYhOgwiAvMZ1RNr%2fyMTK6nru%2fzEvdgYDQrneozUgmEgSVCoOHYJ9XG5yzyGXqap%2f9hpX9nBFPLhIg8jlvjBAUd2cBDxMZ%2fhucbKzasoNAGzk4xzTitrPeU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Ku%2f5quMQF6kt02v%2bw6Q%2f5aOwOTmhlzLpedpP4Q%2btSc8wSAJlAechM62m9ku2t9f0UJsaRAq87dyuSx3gqxWeoEuI0lOjmO1yAWqKbb8rp9TGW5evGwVa7lK0uBDXW%2fMuR2pel340sCI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=m%2b0msX31Rb7A9VVntRmCkO9iqJXgK9nORHcIi6oGXiE5cnUm1k9qYZdi%2bIjj2N0f5F97D98BkCf7jzwCFP48g5Q1dXlbJ9JS%2bq9yATJnskV1DsOeoDmYsAqekgO2Od7GbvTvjiuSHZw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=RRZ%2fR3ZY58OhWAz9v0pfeGExFeOnP5Hi3Iduzna%2fuomutSEJe9gTTN7CMdbODf1XB5Bfkz1PVfQXIzgvDFOoJFx2Xw%2fKvV7umhwqMW0ZpHqHJziJljMu7Jg27NTCeLn72cuJPKhT7Dw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=6GeCDG1kjIJa1lsF8q5PU8YtF49yrrKRlnML3OB0Pby9v6JqXUQEgfPELddwqBRqlszpf6Sn1VDfSte1OvTcnZatFLaerenMJBiDZGL%2fIQ4hSkWUphyD%2fmwRMcbdqNy7xYzQBRd%2bvoc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Y6cD59h2or6TKBXDJMJ5vUexBxmLufZnSLh5jpfeDexuCoWQe0SLsFio%2f9WZb0oD9xh3xIJwWYsAPLDDvWmfXdyJv6XMaAtPU7QwJgkjOAe8UHdYXQE4K%2b8NVcPmG4M6iwHxsqgNRXc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=virBvO18i3%2b5fyqIlyJtr44fj9FGMfXT9Orwloplmtoca7%2fYd76NG%2fn0H7U9dIWmhj1%2fF76RtI%2f3q5eZIlgC8c5SHILJ7PVq%2bOQ0vbtwGKD9EKXoiBixjTo601Fvg%2fKsAJhOsA%2fHcZE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=GGYubnLJOILeLxYTBIAvsdhGLvvWrBz6m2jo7rAg7Sl5xCfmkl3dHv40oA32Axlkgw2bzfjS8Iv%2b%2bpgr8jszeenK04rBTQdAy5PYHWs8HHtC10IIZnt%2begmTuPhED%2fcv5w%2b5sa4yRBs%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=nQBue%2bH2%2fLTkSVfpg%2b0vqu%2bfOFy9Xwp8Le4AvQrU0IJAc3aySjK0NIau5xxU%2fN30ORLknbScJqNhpHmaW2NwkM8R%2fo%2flpETRIVzr%2fYmswHSg58BNfK%2fJYTTa3z8uLUuzpkUs7J%2fqk9o%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=FYQK0tllBi%2fUxTQJWWrygEOoJT41e7I1iU2%2bj1cUj%2f1FRpIhTbUKX23Kce%2brZsjU6gpBx2KVQBtQ5xI40L0%2f82U6zqbvXpileWPKC9PxrPpquNftknFauQlSrPUMtV9V5lQB3eauuAM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=fra8dYE3FMEDTcfP4AIUmmkCyWq%2fTKnMfX9RGwLm6zpUOcRY26UZxfTyusEEiJC6OC%2bPyfy9CV3WVaVfDLAz%2fP2HKyit9VSKLMX4JFNHgPx%2bjA2%2bY3TBh4tZG5JkxTEDmeOT49%2fkGF0%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=jyob6RoX7I88BUVW15wmRCPwa6WQflM8jh4%2f14ItU9voVeKdTq8%2fSo7D9FMZfnZgKRPiCdoqs9V6BgggAcESboAfUJsMiavMD%2bsT7%2fKZ6W7jwoldGr5q26HdnYUdAnV3T%2fXhXckeCbY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Mrj0kU%2blod7ltENrIzPJqaT2ObTmUG2INh15j2NmT40rGF0qtZZtk7MrNJdHTT5aY4yTfnQvLbqhcEGaApTtyhSXtEW2Tc13USdqDaH4xhONaa%2f8cLIJcOBXTsi6977j0VM0D3vLTvA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=xo6zBx5zUF7Im%2bZl9HgCqN4vS%2bElUOcaMTcUYp2aPq6Qae06esfSzPvyFK87QuU7usb54z9FfBMreZbH0FY7CJtMJ7Dgvoo4RHJDhEDHxvZsD6YIumWeGvNLGaVa1Lfd0mWc9%2bqnkmE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=sqtlohTdjIomhsbuiIqMGomceQD7NjYSUOqhP57KwmP%2bPAvGaYHO3VERTGXTYVWBT7n%2b1n0QkKErHyEKIFzuqRAQ1FYzSvDBw%2fLYi03ZBF7zMGRkp0Wytxxpi3J6LlTE8debQjF%2bdYg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=ELRT1%2bq%2fo3iP9noHkb9teavC24fm2FIYWCkI1FyoXc34CWbo2fo6fAzvrsqOqKhJQRYT0HNof%2bu75kyqN9MNot75h5XQ7qALKwBsy2SmcfpEXFDEUf2N%2faPENND3hvqqb1T%2fxQCXVfM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=NYgubckS8FZVYtzC8ALidK9BPNFnPLJLE45CYuF2PoVisoEa463pRgb3jpCHX5tsODtgUBi5cv5U%2f1wICfzEc%2buHhGLiIltuUOQ9kgaERKoS4qYpU1Dl%2fQIPodedFm%2fW3JoAoMfj%2frM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=BQGRtt1jFMsEejbdGncGql0lg0uhww6uLPSipMUTpAahMkwXvGX%2ffHN0aUaQO%2bBy3hEpeztj3WA8t8N18hH68zvexZrFCf7ebCjvxUDvZWkEGVHgsKPFjBD2GJuQdGQj0bQxHCeseQc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=mQHey%2fWcKJslofuSbOXNxRmDJhufvbTqgAQhe2bMIxv6Lf6KqKfg8w8xiz53eB8HQkiqNCB6i7DnAUoAi5RbjN9sZztT12C5JvUJzBJF6a7iJrg%2b1NTQxIGO307VyX%2bh9IUKcAdrafM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=OlghWW5r2b76ySVaZGF66p9TvhlK7wy2a2U2%2bO40qIECbjxEi0OytGxoN52O5tPwntYgmJ2C3tz3P0sbhaL9HQUictX0PIgJFyBsvNJ2BxGSl8jzqFpfbYNz4vNJaudfBPCEyMS6%2bPc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=vO7Cm6fPJ4hf5s2xr%2fBSaqEaJ6ihM7%2fqjHklRvjPhCD79vGoehe%2bCqZ8RVTmkmj6rKyeXaitNMZq3dbyWbpn6X53Id%2f8hxyqZLaBrz9uHmvpSxwYfx1w2zZU1DwHJkngiv94AGiPRhc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=for%2f6SUIgCX%2f9xcuTYh%2b3HVNq4kehov3mvYLdVAVpGSfAzFqHAmH%2fFDi2ul4mYdi66aEA91di8pku%2bE9B9PhfZ3oKbf55oqMJZtarSKxa6bMnq%2fDV9Qq4uA29dlNScH4uh1RxlEaw44%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=WR4Yudm6saWe2opk6D5d7jkMSLyMmVF%2b11BtnHeQYB2QZ9eRqeutFBuzX9bcogNrRdNbhPqujLzE2eZfiKwZSGR2qt30X5K14DZwaTgYaRjFm0HV2STDQU63k0TwShfhLS2GrsM3Whk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=929k13%2b%2buCEg8EKSvZOaZxVpPjw8ybL%2fkKGVNTMs0PWEE1gao0pJGaJIdlCUNH3mIv7Fgq9amljsYpWjjdcDVGWW36WIcfzktJBMzh3C1nvGGZoEXoOjCkr7Hp4KDa2qbX9kgxTX5yM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=E31HiWhMNWFFr5U%2btRkH2GBmBDjHPYTup%2bfWGFlp9Fu3RWA%2bcCR0ZDhIwkKX14HNNlxzi747S2ouBLKskMtyYQPm9uHYeFuLfCqvN%2fHQ6cjq3YU52SR43owAZQsq5gQyaTpTKFnFIuo%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=aIWlGy8rUuJBvvUwZ%2bc0NH8uG%2fmG64od00pxWjWw1FMLBCVOLLKy4Vavfwf7ofF2KZ2snQnGWq%2bu%2fngoRWBUkv6NQD2BXon9HUH8aZWBqRXsxNpdL8eHFsZ253Zf%2fHhkVBLxKyQnMZk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=3eL13CjlpCBZPFJXlGtv9jG40mPdF14GV13itde9wxFmDeOfrI6ITuAxPrUrNvici3bzvZaxGyLfMmbpIY%2fEfP5cjukwu7qF5r69R8XOYg7%2bnt6jteFriQtkZZH3YOM8M2OucVkWbNs%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=lGlrv8MJXqeF%2fJrV77RT8z5wpkOu5nAzEutEqPkr%2fV3uSoJBa%2bNyeqQql40vXn2Gxo5Ceks2mG6z4HyFY4KFnoV1A%2fvBtkRpZexcIgD9IcnGnml%2f5txgmNwDRe6PQ1twtqxxOIL6mhI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=X178UWfZyVrIMnTuYFl369JX5UFqZbqwT%2bJUm4PowTf8Gx0TQGn6G%2fRDoOs0B%2fe5YQBxw581KOnV93qO3%2bVMsN2vOYBa8eMQYqRgrmQDu8zgfd%2fqqtLP2s8SJSWgB0uM%2b0A1FnotW%2fE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=t3Yhhj%2fd1kmviMMah37qqY%2flLA2ETZ3%2f1X9CK0G92mkRDZOv9UTpKph3XalEQz4C7brSrxWDPnIqel2MxJZ8D4r5YH6d%2fYzt2uhG%2fPmyMLGZDH5I9b%2bkfOTyrani%2bcyvDkms8HKRynQ%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=bFhZAZSEVL6X7Y%2bYJ%2fJVAmJYwmFOlvSLQrhG%2bkWcQZTCnGMsUOsMnbpn0w4nqI2Vl%2fOxMb8%2bMXylROVWMKFCNQnP1pau3xfFmoAEYSaVjXt1BCbOHZmQ8PvTYH5PJpK%2fZ7QCQkQOfqY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=ieXLJYiV3BHEsC9lP0wIdKCZuxLp3KB7hjwbdu9qBilo8eDn%2fH9FysyOo9Py8PopfwhYbN%2fbwPXeTASYAPol1Aa%2fWTkyCbBDgwgDhm8puIsOr58i9PXmcVbcCqGWOEVOwS3PKZNMW3M%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=iQnNx2UjIHysZjUW0hfMB7jLvPSML4hwI0edhnjT7zPh24CzjU9dH8SlvKLMbmF9aeVbVggoToJq65ZnjrpuPcRURyLox3Rt%2fo4xqF6ym0zTR%2f0FcUTwA58ZwDn6yzvuom%2fBbjBLnnY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=a6hRLrPRb%2fY2e49K8Uj9CwoIq9jX25%2boadeIv9%2bBXb6Cy1uepJtrGD8w4Vmn32qwk5OybclSTWIsb86wBS2q2BAxilzN90bmG9roj%2f4WeJK5ESMiCeI%2bNJ0nWSECAHbsEQbDaCpr0%2bI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=mQSAtKSonOqJUqCQwgMs8zIV4FmjEtMJXT308JHKbnZbiWAVyD8Fm5mhSW0SCHj805VIV%2fRAjfV%2b4UmqoVsAhfX0sw9J4Xy99OEBy95EngByZuW1hVzj8guFHZgNShpBv9Ov%2bjChNoI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=1osIO2FHtciIQfYyzXoUOw0NVCi6uESkKg19v56GPbOUpOUK0WJBOAvqzjofaZZ1lYbLypbNQLSWYSXvpaT49g4Yszet%2bt8fpyRYlPEFozAE7ml6dQAdlBBzDljp5YcIZq01%2fUaoSYc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=lwUDr7ZFsrL8s1Z61NcI%2f0xjZtD3WxkYNAq%2f4II0FKOzttzpYHgCGmRkoulwukDdSO0mmb%2bJniDvFl2K%2fTWHxtgeEbyNUOXLL4pfMvt2yHsN5bmd9%2f75AoZJ7XI4DrYUPTRPyZFX10Q%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=E8xzM79%2b3CqKL2kv2wa%2fgrhVmfZgiKcK0V33ts5ADeeauwy3yi%2bFHgJRKQCg6KFbFrnqG3wnzv5SLps%2fNWJwcZhoa2XmI0euBlKACRWgjoF8yC5iupVLC7jkyHyD2ehtN0IEAaj64DQ%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=UrJc4Z7ZXeKzPjVFp7Qq%2bZHxDRKgObXbLgZ548bDgTOpGx0NA%2ffN20GFLh8jY%2fufJA4cMXXAAGCpjPL8GSB9lAgqxeCjQarTmcEZdcYe%2b37fdcgDGebDWpTyMdF23VN182r3Ksv7c4w%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=0vhhgATkFmRSFB4eS5fOSgxYhUwGvj95%2f2AUfGEdlzLhIo8ro0i4vdCGd7uXCn%2fFjh5pS2Pa7L99LeakaHn5U3tDOAu%2feUY5zwC0Yv1cSD57r7mWZngICwBauncrVwY9O4bfRFq7TyY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=fxoYclP2L%2bMoQjOBVd%2bLZr5DKFwtDi0QzwMkupzH81lBlHJxysgYRZqo%2fK%2bS1dqAeYV28cboldvlMjU%2bJuXSfVNqo%2bgxDEOlV1nwzPPCGMLQlXG5vgV8dB5Ho5zqRmXRzOcb0w1Qosw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=QgJdnA1WTdIDVy40SspSkzMGav5nX%2bsPtMUv9mE8%2fefJPlgbDS9NRZgBCx8ndpwLMIZyV3SYTDcFH67jH98XEPrI4zQeAOPaCLkLl2a4nqJzfLkBY5xhDPVTpfy665bAa%2b6oZ5ZBaWE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=A7pT9bi07luy7mghxoZr%2fGo0m9JECLdw4vUF1UeQlWFPFCYI%2batP68lUARNK9JbigtvoedY4dth2tSeMZqtblxWRJFOjCfR2CUgc%2fd2qyYNFKrIOTOkgQ0mJtY%2fatpV5rOccePElcaw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=sH3Ct6%2bdYZeC0eJ3LxSWnuqimoWsDm8CBQYdQ2P8nw6RF65cb3jIxmb7xlRWVTV8jfS0MU%2bT07%2f8JaI6yQ3bg0WgbbnznhZjMqkhhDkMxzRf8tN0yaeqQpGxyu3CaqiCj5SHBVV3UPk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=lB9oG9YlN2Vu97Sc54vilAXn%2fe77pzf%2f8RZ5npgLNGWSyR%2bwgdzeUsgoN0bBmx%2bIzSm2j6LFKKjkeUPT6XpqpnTSyLXd2V4H2bJysAr2zWwGAmaXQ7nyyibsLHizhGrZY5C821bDR4M%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=3X2iw63YfcUEYoXmsf286YzCKw7hZKpxxgCR95MjtbN0vA%2fx%2fOOe80hc8%2fO6EapRaVOLoKnPLxBn5mYQBN7fo9nWniaoAPBqREFqHuSPjVj0KvYYHtsMuAAlBiy6dOBpeh26YXLOMLU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=nyBU%2fUHw7K6PAEknpnQS%2fCdzBmvVGEoG7IublD1xZelMH34rciTsAPXHWT%2bAGkyPLEgELQxGWaNchTNj%2bCkDNVbNIe9ugmxbAwNsDkMYXwI5%2fUOp%2bsJuGr%2bMktOgn8o53MJ8oUjEkxU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=d7DXyCtDpbXN2imN%2fHIstORUo39w9%2bl247Hb7VeeV06r7ugOqVop4QdexEtnKPEvT6SknqG0CXx%2fBb78HeftFTPcXVlk4aCGhP9cAGLtyh5Ld0pYLV9aHI3UPhvcIpGdKT1Ak9HE6Ms%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=WI1Tb3vXu1xABj1T%2fKfeUgFqC5OTliR3WQ8Kxdyg9rYl1bxDnkeVx9eqHjl5G%2bDGr09K9D2uLsxaYu6mZawI%2fIOoENCuNKuRai6wOo3U6YiT8njmnsPvyPGuR%2bqWUeM9Qd%2bV0uEcsXo%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=zTAMLGctXHL4Dm%2fwqeTSUBkt1TDc4Lpx63rdpIAINiZZDxLmtlc8B9IpSMG1ph0ocqGksIhueE2dbJeGUO%2b2OXHbHyIDMSUzjHumvJoik9rChZr%2fetvmEoDKjrL1dXl%2fXSYO8J9EClQ%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=5xIVtftUYvelRqIOJC26vfEWU8Ub7PcEHB7t2%2fNsY4yP%2bRHN2vwTYq0N1N%2fHdA2L%2fqTrD6dp2Ac%2bWSFcKQ6hdi0VOCJ%2fGfCZZjGVpmvGj4ulafQVJ4x7OZK48ScbaY6OkjYyd2WwrIg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=R%2fBr%2bpqMhqmGerbydMn1zIpVC%2blV44%2fCgNV0cc3ohiNaxDpYTW%2ffnntP381VQE1xMg1ExdZ4FmzX4ZdGuRgFIt5CRDhubhQN8Qi4QpZTxiZYfHTm8YX4A%2buLGCxBgXctX3En%2fdvNKwg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=O5FiTAi3tLcdcPRj%2floHdXG7pH3STCtItv1G0qBM%2fdiZS%2fFCBp0jKrIMhfca%2fwZ4ZYukHG4lWjd2Ko8%2f7QgSLXHHmyX5aiRPpHhRMrs7HE7P4vq%2bMw35RTigwmw7AKp%2fA5vzlc6sHQQ%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=GkQ9B9RVT8Y%2bjEo6PGvnsM5jTIrlnNFxgtQuSYR15f%2b5n4ZiF9%2fEIcGKz%2f6vYyvrG1rl7073JyXLhLvOmF7PsxJPnq5tyTE0teF7uq1mLaI59q0WX42lmeg0GCaWsBONKMMTL3XLNKc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=EbuMz1WYQN%2bylj6uH7fi4njpHajIlsS274ul8%2bU0Dg0Bt6vQQB0eS862Pyvj45ElCMQS%2bmCXAm1Go91aCP0zmICX0peHKi3E5OjObqHZdNj0HJQC4M8aThzjy9BtglAjiuIyX5%2bYAfM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=ZjTZzNOzMFPQRC5pj4ZkO8VUPDvcjDoBiMx6LabJs1ZLp6804XyH8yKnHUJ%2b9qjPyUn%2bb849%2bmPvR9vFAiIt2mzB7z1%2f5ONAiFY%2bfdFr4u5IiPsdf156pm88%2b2ynmeKImCJl3j1oWFE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=PpcCfcbqbMWA32jnAV1JkKGIEGo58EuBVBY%2bWrTMYM2bIvcgQkazogJI7n9IXrAZ%2b4C7KSmVwC2rhk6sdEXziI2CeOVpx6fGMCF1H3Ms1S78zdl6tQ%2frk4NMslLKpnKBjAlu719tFDY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=aID4qcin03GSZeNgRqyBKb5R9ijmFv9D2qA2XD8qSQV6BAILsYLKR0N7uyR4e3OIf3aDrBJXNe6QoHhZkIV2xC8IjAutCk4%2bmd9pyQRztsIKzreY4NmyX5ovbfW8eVJeDbqZgKtCIQU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=4tMWADKs%2fg933rcTOkINIeBb70du2xFTCLZwkrm3ph%2bUXAF3vD3thzzPM1w8Gl6GxcnqJOPjLUoKXgJb9AV9SxJfGiArOdtCIgydbYvBH9hBFPTuFgYwcYzGhpBUlCHfYJbdrMNQJj0%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=aps2H9bPlqPZKQQstVx91CvqIC%2fatZ8SZUd0JRu2MPOmtvHn1ztS1D7y6WNGEvQM%2fuJ7f7Fb8vuRH6B7e7Ado3o7lKKPdsoFu%2bW4q0Cg3WgNvbkvYp6Rug6lsU3p6NJKxryoBfEts84%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=WIQTzceUGbvM%2fJltDDhH%2fjpNot4wSX9%2fAig%2bt2brSHUKyocyP0YNIhJcVpkk7e8pTPbXHUpRpJD1wylYE6t1dvf%2fKsfG4VkiXpdghTl3KCRuxeCeuGQ0ACMCWhsWJK6Ab88K%2fYfgXm8%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=7QVy2MRQO6ZQilK%2fropc%2frF7YitiBraimsOS2E1krwQ2xh5dCTOCmtrCw07GKpQRzVQWTspcFtK37r8DH7ZPJzamm3grd1qgXNc8OCCiOP7BIocCkv%2fD5rRP8uyRLcqRI7rH0dk8IX0%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=q%2f%2f%2fbNWKtvHjyaiSuW7Ayt8qOr%2f55ohyhNzN1fG8O%2bBzYa36%2btbNurJYGNvpK%2bN4CzyaMORb8auR%2brs1kibk5V%2fP%2b5VppyKmV8zuwPUdrhB4gTWsgIuZGVnbundqaHEsDY43N8vw3%2f4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=HEtVk2X2NHbTxQy9EKAjKB15o4euoXLN%2bxm1nQuuP%2fDWUfNLpv3qLsMa2w4XFijEX%2fnCi45OcT6oZP3XTqVT8QASJzV2HlUK2KeQzNAdCzOPyTLLxs8Dt9bMKwk8Hn9wHhji0bwaVww%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=9KzNbMzRbPJRV92J4zu810YhFXqativDOpLBsLAKDsVPqTeBfDkH7sSVcsxmFgz9ahlCBh%2fggIPtoaR7eH6luySG5I5I2i1YZrruZz3U9KCB4nzzekqBpSNyQGVTaKIZzbSAY3jjKvw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=7JL2VJFJc91IMVTDz6qxXnDtiXC7nWJPc2QEjvfAzQ0hLELp%2bUnC2CAnQ8fiWrIXCxD%2f3EIcJOMZGYRTd05Be01ehNk%2bccrJoo%2bvPKx95iPO3xVE2BLCRUzO2r5ItsYFz2lZK1hu1Bc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=EpZTcJCXvGgXMQesOIcbQEK4QRIOKeEW8SS%2bFAiwzuiFzPZzGiGSGbQVSyifNcmc6SlOXybtIWsujIg8DMpd8naBd30p7EotenuY0wU6cYUbu8VTVA4BMRUo7A87QdeJJKb%2b0zIgFVE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=BtjY5VGwOJ%2buYKNo6J9Si2RHWS8IA3h0naiYVQNI47TFDWsB%2fpL0fGAoFFUCrq3pnR0gYbADxp7Vw9%2bOtVQWiekxjMAFVrf88Vm4%2f%2fQo0zaFtL2Jpt%2f7gWlNjbAhMBau734kaPwuc4g%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=jjUsYv0spNmt7%2blbnzmbKwOflw7sbIZwi%2fNtb9jVsmUzkkUtnnQYF6UdVcDFhxNtAYsv9QkYrUgXJVyiRuA9ZRQJEELNlYI6jCTG0t5zNCIwzEyDRGHHAAb4JQs0tvLcnJqhoN2oAOA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=ggugvuLsUPLXwp0%2fypMsNoT5NoXfQvgxYM2q9gLNS1N%2bMH2X2lSg6jxsz8SS5JsYTdKI0NWJbrl5PujIbuw6OlFZYPW2vadTiWahKjVe5VL6Vs3lrb4H3B0rO%2bV6o8sg2MaHQF1%2bjDM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=UnLjX%2fq75d5t5XrdL5ytQ6EE5EXpdis8C3CJeptGJv7ywbNK%2bz4JJZDYYYnIr%2blRBRgWL5fb0bHj0UqPyz6nNPwEUN7Ph25iwOOFa3rvMUEmecyNsPE9trPkZghDUvWnh0hjDvaXAdM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=zh%2fVeGGtv5dt2wCGEFhqqK3axMtYFFjTJ3cn5mxoOddWYLGkXAyOsQsU6gJF27BkyB8p1U1k5ZKVm4j8PEJ%2ft%2beAbrC8Q%2fH4kWHG9lgTBIaztR8VcSfuCI40Xff%2fPvf8RqSHLNT1AGk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=uFo7ab3f0YEj%2bmWaij8CtrFWGsBPOIc69MNazhQA4jZG4xn25lMuO4wKdcZYW817zhEcCfRI2Hw67Ow7Yo8Gco7VboJPeiPPgENObnXRVRQiwqNzVgkDQVN1CNoluoRq37ULSNwPRqU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=yM%2bt9LisUxLFlk1IIZKKakQO1JEXOb627qUhOD9Sl7JZQ9V3DQ5WJnSvHLB6dqTSUlciVJB2v9GHGBQD3Jlvb5zyL%2f37THJaDgUrgg0Om5PmNBVhTUEgcYAh5K1MUKif5CB%2bRrsB8CI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=wnxM13kkh37toa9j7lsAWbqSGrv6WJjZP5ZnMhbhOe5Wqq09TXG%2fXfoJ9RYqZyXobkmUV22yvRGl2NuSj4IK9BuB%2fMMuo3t%2bhYZLGM2aLKhlCIT%2bG4NX4yv4JFpZEl9DWIhuK41nT40%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=e4e1472YnCVC%2b7r6j2ZH4yDJ3oP32rBFi1NtHJhfyRrfjLv2Nvq%2baPLZDGpYXkz7wCE66wvZAsGkENVMmLBQ%2fzDbP%2fYn%2bQwVQOvfMXqEaXaMmL7vp2evQYVgVbfHPZ1%2fBb6hSHbvAlk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Rboib8%2bZ7NeJy61iBSPYGnO%2bO34e3%2fBRO64qHUG9utIe6bm7USmdaLYObF3io9TKlLBfDhoFcQlmV%2f6A%2bl0gvommGVuG2EsatYzcFb8599gu9ryeIXv6qXc0JcunG39YE3bl7Nt6dnA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=8ayxJIfGisQQK3pPjLlm7nDzx6TgbrHTILwD0GRZqchria%2fWt0pxbshq3wTm8ei19bWXXjKtIWoryaL9NXssOuI19oiUgwpIe89%2fUWQB2G4Y5PD8yGkzxyowxWbl1QFVpXpSjDCdRBA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=vZk4RGofe3b2e4L6UI%2bZ6wpyaHMKUNj638nyjQkmnkNEDU1N8fDG7%2fF%2b2RbjQt2bnxaaTUVomnv2QLhPxhiMdez0PXhvz8fr4FsQB%2bfifCGDVlZklq5XQ3wqHjjnNK%2beW8i0Scor85Q%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=iyt8yuUnmz%2bqFPk3iu4n3RW3cErkN3yCD5%2bO1cg%2fgPYo%2f0snQ%2bNbxBpO8YAKqaWh9N3LvhOiKOUhFL8ovyzXt1Si2bBcD4g4xnUMuhRqJ1BTRBqTHty4sf7%2bQRyBIHQkTctRjvsqSBM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=u71dYmjN%2frbsg8ddHLw577MYkUF%2fhrtFcypd%2fuyuwvesVPhPy95vznncfrqk6QizV4w6c9PVG3PZSyHU%2bQtYZ2RuhI3OE3CEJExqWMesNT0nfmVKGchKz0FlXuQ%2fphB5ZOnUIeiOREo%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=6vIGaJxGw30mg7RCJadwknrtxjFGmOklcFQEiPH5BHx8XvgcsMmM%2bWJ6oQzOYnAblEqbnDyyCS8GgAmct4LU5QWiOSOop1LQ2M9Pk8EpqmG0Dmj6vJ262%2fg7CNt5tf5LM4pxr2SwuZo%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Ji6dtoJt8fnyUms8yAuG87rDQcsCw9p6Os%2fG1SNYvIW3hsDghuo7E5DCytVwu6lfRZjLudhoLSXR8ldgfA%2f7QT2ypGpSS6ACCVdo9lD5ojaP1P7lb2ujfemb72XkRwwuzq9E4p%2bqteE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=lzsIKdzHQc864TBZBNpvNNKQUNvI4%2bSXgFR%2fo7RZpDU9%2fwQUG9FDd6nH8MdWnOyqwOXw%2bdB6zj2VyxOi6IV5JoGX9f7SX%2frBtAfIQpSMPbtN1u6BxwCOUb3biRhJfNfPIhblgWqs7%2b4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=l7hmxOHYXb%2fubn8EKP1smKdb6ocEjVqZy6kpHCecZnUIgDoQmOBs1HIkZ8xaa69Y9MxKIfMGL1QoNrNcW0Gc2yCi%2bl6ayb1nBKKuqx%2bW%2fHVLEu%2bzAdo7aiFSMLBYRRrEZnSdCkK41Nc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=ZF7178dMY5TN9kxrtb0emLH%2fo033c4M9XsKsNv1SKjwnjDU5uwizEqODhswYjJEhHu0UJQ9hVVRdDf35Qfi%2bfHU1e6OJFDBHeRfQzqgycf9I8RIS8paYneciJVnIfI%2b2tBLXOj28r24%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=GYUf%2bL794p2vehML7ES14QjG0OsBJJJV7An9eXVWVH81WLVEKI%2bkHB%2bOTvY8lmhlxHI3WAFnxMHC6ynlUYwarA5fwrCiXjBzs255rogDIh6x1blGa18blP7mbCc1dWrL4k8TztkygkY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=j1KznE99HFVulJ%2bEIk4dlaVhvvx0jMV0dxfjbMVh5oTY8o3Wm4dZauw37ZED%2fu9tDDtnwsAfDDm2CLuVjdVwzTQIBhb%2fK%2bKxSfajpWUFg9wIUOTIVP1Fakif%2bL5z%2f5nBjCVWvgcGKlA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=UrTqDP7sQJjRYuJXnw85hsCDpu6XKK1QDy9edmjwkUWt1cIyOh%2fDnJzeQbeb4%2f%2b0fdG%2beEF1rF2TsD02mBTesqZ3Zcn%2bXP5MFuinBaMhY4ShjhzU%2frifgs3ugHe5it7uj8hsxk91woU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=XtJWVw7VPeDfqQ6vsTBiBMcLxIeOmrvEs9F5xOyCTpX29c5eZ8xw5QeL5kAZ9KBurQPGgoFQTeyjWhGK8YPHveTU2qDkCtsQ8LRzQ1RaQEqEmLNF1OPQLwlRrzDB8GRxkIFxfojov1g%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=UD1bhmLOkpL4zur%2bBB3%2bj25VFYUTwkctklySECWZQ94WWzWOaHm7q2Lxq3eIEHk6dr1fR8pHtlSyKF3fe0AATdmjDXDeQxl7SmIhIRdoamVeLmNMauT%2fjMtjTZHtCOTZmm7gjCgHp2s%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Pw4tEy4D%2feh52w4zTqTguNY%2bY6VbauO7s7UVQQK45Chsb0FYlg9o1QVCdGrfbyW%2f16NMuNcesoekkKMLkqCZOpX4FGi%2b1HI5Uxm4eOnb8c50DRySjVT5WJW5JdFcCFArlKq%2fwEnLii0%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Ars4Upkl6w2rSd2phMKqCKUQ%2f0LLSeFnUwzpSiqfjxkNY9go95LkH69IEnNseAKcDyqAtX3iOejPFgtANcnV0lV5ZdAGoectPy4uNaCrYs16OIl%2fJKJE9Et9jQmqT%2bn2rxi5acX2hMU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Td4jGu9TpBixIrKzA1yl68vQGwPdQ3Dru90cGc6DMO141g2LV8nT7Da%2fGs1WGdcQggWvJxdYa7vzngz5%2fa5Nctig5O2y5NB0veIzjs1l03Bd1nSrQ1jv3fRVA%2frFJI1oqxF084EYX5Y%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=02EHniOzym84P0kt%2fe91I2TGcyqXW46og63xChZfaEWCXrpRo79EMrTImwfdskNyu4RvzIcKsaYVAEnX%2boQVOnsIWdkTwPBYx6Y85lm8C19KNvbnpWgma19NR0WNtYKNCVdnXpEeNsA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=VLyb2zvfNXZtXSieV1rNaZ3mxAZ1DUcFwiuscDOahnxZUNT4o5P8xneD%2fUZfgU4sjHcaeVPjggBPnz9qXSDxaVfancWQ4lTJIysYA5kJCfum9H%2b%2fobJny6wMl9eilY0l8oGb%2fYPXzyQ%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=6ru0ZyVfWEli085HB4T0Ek6dZCXrfQfRF6fKdrOmrvJHaz1nS9DQYJxR6rrQvItvZIdXQNfiANOCkBuClXSqRpFi6n4vJrb99Fq1HZAyAOQb1dGJjPZERNWP7EcBauhXBXLiCBS2cCA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=lFWcCv%2fODNLv1S6F5Q%2b31tweK2YxWP54dDutFj3tgNA73PPe3oxvZgfCIQLckcKeuAeqqSdU0ItD%2b7y25MPTYu4SwicWD39MOIuPY6zlgc6zU09YFFB81vcTP0oLmsDtaemvXpHVpQM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Xl7jJPk3XnvTxg30wqC33on9es%2fbLn4ZmzqUuLqJQCEfY6gp5jaBrIR8%2f6FZ5nOp8wLllPXDCOdUgo4GA6Pl95%2bdUZSilN6p9eeTE4lXInSHzGDBimJFJ2xEjCJCHCic8XOcLhsh%2fEY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=kQUKNItf5IIQ7taAR27iJrxtNnlz6iMe9nzT402J4Xk94MQ9DWZbU7bE5W32auDV%2f0KotjUf2NSMvGNgbM0xEcfpTB1%2fl0rpOWI5zgCXrN2kTTl7tUVaMTXv4KagxZqIR2s%2fIhVICBg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=EOQPo6ZqZfbjzaafaNncPMdS0n7%2bvHNIlURfjV3XVI3PDlXSa%2bDnKplYedy%2blB0uqh%2bEAnv7%2bAHJoIDjBPNYYZ1zP5iW%2f%2fiaAfbN8i4WEIHosvtNiSFSnoY9FSf9nSHqYu9nxkXpUqk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=4aoYVszONwc5jUR%2fHn425aHvRDMzfBBsS%2f4WHqDp%2b9Bbu9MZ3O2Mbs49OUW92zcSGI76hTw0q7R1qJtnVHlsO4s%2f96gxO1FZy%2bNB%2bKjLHiQru01g%2b%2fhG0xkI5IqO042cjlkJHs35NE8%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=pJhmRU1xeMosIIgohxR%2fIbxCals3GuqrK2LfSpb91th5NQTMEP7dUoOViGzjHGL15hABzQJZ8eolWhIFPy9IKCYdmSpfufFUzAWY5EP5jgm3mjO9f5uyDkMH1MzlbDbNUgxL9C1LDqc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=PojExtlasNSzOb7ardTBieFOVEp%2fkC6ekTloDecI4tAJ5howpFEVhguby2KJKxS5GDo20AUE3gUq%2bcbtUOSgl3O7FCdr6JW2OQbnOiLP6kTvgf5vc%2ftCJyqIZsweqWcFTtESYQ0rqKc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=KhOXd29dPyDBZDyXZ8a5TVjwZvnUJ1wbT2UVSiEyBGEn4cfyMqnT1Rp7fIsh0b1OsAD8oa5A3xVmnvntTeZvX9QVm5z%2bZ5Q3AYNbLL7bKQGxf4F6OxnL9HuEW4JuIrIIJdlbKdVQHSs%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=1%2b4MLVA0N3%2b%2fpARBQx0TapkB2pOuFtD5useZhVfUXQKO08iNzL7Cr3xig4GJ5lvpb7cxQcOjJl3dB33aVtTxljdcUk9%2bQnOqE%2fLwHy59NTzjSrkbOos07n0CjTHmvTwq340l4g6r2As%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=O7FsS%2b9u4LmIuIdgMoxlOMob5acgU%2f%2ba%2bmMlwneakXrWSoFrx30hINTc8j4u3qxalAl8kBdeZ3rwWjuUuGo77TRSliplVt9O9Z%2bu5ENGIxbB01Cf4rjzL13up%2bPkdFEr05sEFII956A%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=2SGq5CyEY28gwOz2%2buCnHbrw%2fMDBEN7Bj56u75bjyo1IokdieFq7zEFfWsCn8%2fpbBkZNQbnz8V0PQqWFACL8yefAea959Tsiz6pU7fFfBkqsgYLSGvecTKRNHYHfMFhwfBtATi0KQts%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=bL46kZbRw%2fOhUwhPzQeRRuInbz%2bfNlPkjEh%2by9XKDWqHd8uhhJir%2bfeII%2bGqLZNchG%2b4lsgtljkx%2fIN3o6HTaEcM9ZtgVduR7HL5OEYXlsHUQTh1p7AsExVbhUv08V18FNux6RAbnVE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=mrqJtZeEhSLS8sq%2fVxDF8au9lbTLtYslA8VnRFXxi5rEwDg6wAlogL3jD89D3JIRx%2bdJkzWF8yVCQR3SXvWPPRTY%2b37puIAXyVZMED%2bw3aLAbo8cbBvx4P9DR9ixQsyUNTL8ocqFQHs%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=0HaPNmnN9zyDpoYmvbZcCkKJ%2fo2QsGiWV0jTQfJ1fieZOZ7gkz8w8kmznRMRsaaoCVwVCJFEDgSwONAOzGWgD5bwHE889MkyZ%2bbmtTsDXdmzTJ1qIjoPgGs%2bN%2flKpqCsTsoanHhYiUY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=q7tieCYvT9ze4Ly0n%2bdrTcj9kva928rTh0%2fTQXuCHlvxO4cByvu9rgGerkb5wks%2bUOcw%2b8DHQ3CVlNwvgdvVGJr9M1icWF2Aw4vP3c24StjWFwp4YfnDpnbCpaYbNsitJaA8g2SC2ks%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=s8nK%2b%2fCdN8C8mzw4KV3ZjNSN1vLU30haj1WQdmpIKL3N16gGyAvmpOF13mu%2bEe89wPWDFhppO6PCRfIjTpx7Dz5twwhxQK22pyF0E04HSNOUjQ3ZVjK063%2b8Y0wJX8lQi1IjGdjZ7l8%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=lehlbU9fPkagHqY%2bouBLA0yVwGgMp%2f8BG6lpM%2fCGCyNvU0kwvbgG4rC9Qn6suMlxjUE8zJMvG5Bm3BnnZpGLMVmFpGSXuPGcG9hn%2bks522fkqDT%2fjEXy5Hu9UPtWiqbPq%2flu7YMDNRk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=YPE4OD5u8Y4VXN8OCSQcJjN4EiMvOulLBquj5TANDDF0k6NslUsxX58xK3EzpV%2fOoSJJPciy%2fwydapIE8f3gkwbrrn68v3fTTSeuD4w9D%2bmcqf9xP%2f58K%2fPYiZRBvEq5bM4gPkjbBW4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=7%2fgAUDwIIuaXuWHG0dZR3spS%2fXsSiDpxnJywrbUMn8v%2f%2bqf%2fo7fr%2fbw2rthNrXm47gfAGKcmpFetb3p8cjqMbw4AldbkwdrP5QbvWqz2QA7D2hWwdTL41IeWREOT2QwwjIwCHDzViHI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=pq7TuBYOsBya%2fPoiFLmRiwbnytebYhziQtGvw7tV5qSy%2f5A7gAmNwvXem1nRVLXBFQ3SlXGCzXbdkT2g00kmNytzzS%2b2ffN3sUKiI3kUaZC0ORz3kqXE45bsi0xRCM66e9shR%2f6cC%2fY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=wt017oYIszDrCPOX%2fOzfjGtTPcR6wvEWqPbjysFaq6clUFi5YzTNgvmtJkx0krUXE7IF%2fnl%2fiddx8AQu4516t0FywmXrWde1dyuVQbDn2KBQYnZKRq%2fxeRVPuYxRaxzCm7HCEFhzvAU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=qsiqr7gsDBY9XCaJ6atS9k3%2bH8nmZXYCh%2fXHGQfXiBHGFgvhIWhHS4aX3ClZ%2btDY9n72PB%2ftoToPdLYcrOLhpSYg%2fikDOZUqAS6tvH09cbmDFjyWx%2f%2fRpVbBbY3aTGZTk8LXjnpu5MI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=sdKOfO2UOhMHNkrBaVG77cZLAY4%2bRWSVzEAxhQjr09N0TVnwzBQopOPc9%2ftmsAnUjoAw3zZ0IHseLOz2x%2bfU9xWWXCZUuEIj0VPGaaquuPh4zECiHFBo18FfrDiq6cUw4WDK9B%2bbUJw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=yNO51LX9wz8hAJCaGlnsKZTqWNdCie%2bIGyLnXNpAdqFqPF89vkgqVvoBhEd5wtgw5UNwh%2ff2uox93eFGunuJ%2fRDP2hnfeLhydmiKmqswsZop08xnK5IvrupgcpilYKywq8V%2fYhnJ8vQ%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=SkrRZqcykUPwl1Xvw64pS5ubnHqZXs%2bol3%2fOpNhVgrbxkPdZaCt%2fJgGnqIBVHZAeLc5aJjpRFOScm%2fOkLto7Kbvynq0mhPuoXk045U2zxlUpnF5YCDqIH%2fZ8k84vS8ZbSc8qYM4beQg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=bq8KG1zFfJALHL8Yv%2b3KhTVQq0XeF8CebEE6v0GgTzCsJRP4Xenk5U8b9VLWLTm3mn%2fzEHmHqKNodUsD1aE5m2QiLZDriR%2bScAvUNr3oQvk5M4jNTlMJCSiKrF8qpHKJPsYB2n9Srgg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=DlUykyhmyzKLLTKkJ1M95fom4n7m02CnGTFogaO6D8i1k3t9Kpbk%2b2kAPxzgjudIEOHZhe%2fyfGXXd%2bowbIZf%2fvk62Vk3TNwqqmp3lFpE7IExqssNIapu3dJBFZFvFIaDkaWfYH80ynk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=kq4s2LjdEec3XjUcRNJPwYeOqFGusaJ1eYHLrtrM2LbDY6QRZ%2blczPmpp24eORVpOWbBQawJzNd45p3ZiZCUliD%2fEfneaCSA1x9YhTDpGPpCrrOgwjnSy8CEE%2bQA%2fZ3urmhZNtlVpD0%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=0e%2fuOYZ7P4R6AbxRURgo5gxy%2fxAg%2btT0d9P%2bJjxspcp%2fHzx00UZbInUS1dHUCYDRlj%2bm5A7D%2fyAsMUAUhdZpGhQXOzZ1VObA22Wti%2bFTl9XDrNJGQi3pig2gLM3kfrvPcFaD4FNh5tg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=REYQFwU5AXA0jkODigmxLY%2bBRAyyLSWBsrD3j6eFztz9I63nt%2fYe81L3BLNjVmT9Ti0tNA8rV3bzspShA0J8RuXeSeCPyAysDLKgP3zPc%2fZuDfYLn3NNEnj0oNLGTH9jgVVjTMy6ARM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=WWhmrZXod%2frND3ciOHiAMJnpy2WANABmTk9q4nX7Nx%2boOi0LlIqOqA5VrYdncALBNacuQEOEf8DjVoSVJJ2HJqo8Nu6lxWSSLdSgO1s0YcXOoVafuHmjVTPCx4pRM6uDaGpBpG%2bJcHs%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=7YaEjAEn7a8lhSgb42EDPvNVym2Zv%2fHuY2btYCCxij3jo2fXwrxvZFUqBWOa%2bjSM%2f2z03zt1XEVnhK%2fjx4jYEhoKWyOqT1mw95XCa%2bzJf0D3iihSSDzpcfovJRbEZ97bplHZd3PaxYc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=QadnqURdy2nAAbFiQBhXMrcnCHD03mquWDgrSMQFWoq0XTrqmY6iFKhxOMqP8m42adzvKYhiQddwuN4uhJCzvokEot9vpHIykflZJQ1EkbDiGeo73nlciG52RA5L2mBsFrWomp0kan4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=1ddua38O0ACnkSJCCoknN0oBCemucdt3IDy71Wu0%2fbP4vFkvGCBjVxHBEPOjl54jzNwVTH6ENFZqqc9VntLQr7K3Sl%2ftAQllwP10JoFTB405OeJ3QO9aGWdRd4GRRxh7opD5H5KznNE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=RXcS7KhXszEqsM9JaKLOofyucKHclSvspoO5%2fZbtYFr2W%2bJ39Q7NH3BRwIvcwfH3A5dHCITk8nCHWCJAaE1JBK339%2bt5wHUi03J6R1bRmm2ZbKEbALIq5TOZkhU9qIOSKMEOfGufIjU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=wmbDIVcTo1v4xqcERbHWyzYWvQcT6VLE7V48ZbuMeSXjlsW0K%2fy1bQfaS7eBT0%2f4tOoX7wtK4s8fOUcgg5%2f%2b0YaSusvbacy08oFvKPo95aaMgaMsPk8a6jp3JRtD%2fkxXTKR1w%2bd9xCw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=RhYn6NdjxPV9ZyYNWSwg2rdKeM7Ovik55ncmmIFZg2ic8%2fRxP%2b1l1FyTP3F0aFKva8cd6spEBUUDMak1Z4x5TMUxi9q4jPFOrdV8FSd1fWMD40cqzgn%2fc%2fRMqmYe07O63kpmD5dsEcc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=7SzreR8TL8%2bef2t9kfgJ7RWKHOljRP1GhW1VxkifgwTonLNxWSGizJ3yIv8OBvd6mmCu5OuxmhUYzMXzDTrxeb8uFPqfdk5wDR%2f4kLEyQqLwPLbuE3NhIXGCIhLWMJS%2fsHHsXWa3WHg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=2R0F0oh9oQXYRnibd%2fp09LlBlaCuigF4kTfG5JsVoWSpFYARLK%2fxWfVm497DRc%2biTtmSU7WRUHlkJQnpbdP47mJfLdx5auLnuhrrdSZwq0pxxHduvbQjo466dOquufu2k%2bLfy74tCOI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=D0zcVu52IL1KW4HEYk2ZS%2bD6PjZUne1SuzDKv4Z7ubR7KiFGK31nd3AuRX9CnU2kfvsDdD%2bXF%2bnrGKqH5RphQ8fEmB2Bzxn1m4A72%2bz1gDFlI9dWcKhpqwffhLecIUf2WeEUeq7RXvM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=8Fl3l9xaEHRWeOtMs5%2fLzbZnX8r37M4eJx4eNuiUgkxP%2fo2Sodgc3KZhJ%2fmSKg52lxmhBxeN209ZLcrNckBfQxHPfTZxNS%2b4TJzUTdLmsNMc1bH0IhEKAtrkoIIBm5Z%2fCLtMMBRy9Ng%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=GdVjB9bsW385d2ZanJ3VRMS5zyLjv1yEP55%2fVeRkYix26w86ungzo604DnJw8QduaUoJB8vjG6VXK9LySpGS1zrPLE4FnOXlRyWrn9q6QCCE6SEteNiLDgkd9PFEulBeOlIq0NVNoXw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=linas%2bCZXgvC5ps7aGtDeyf0FDtzz6nG01D%2btwTH6w7RY66DDJV5N8tWiOIk1oNlCtD4kUFfNnNLTcsPIkPQc%2bjZ5asVO%2bcPZHUBPtMEyqEp4vArFfm1IpDIXycqejCFb341CBkVSXs%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=YhstJNpwvftkdUYDucLxPTg2Ht2cX%2f0uOL9ugkhvT2TgAAgilMa%2b1A%2bfUpkrrSE9Be%2bNit2tv6r0NjTM5JOMgJ%2fvUWLmaTWF7znT1qnnpEYGYQ3BDHQv1bhPAYLx8nSApLmLbNceCuU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=CMI9FbNGolC52Gz8sDC7eVqg43GIkO%2ffVwSd5n8kBpaWTahZ2KPvAkJB8qrWxodif9dS49RgdvNOpMi%2fxXxdl6fVUjt%2f8RG6v9%2ffWC2X5GJcCM8uQalDLHEdKsC6e4yH7765DwgbUB4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Mg%2fX9Zo%2b4s8IcfRUzFq%2bBe0WT3SdaOjFUDTyr3zNj%2bcvPukpGriEgE4P8xVZgSQdL3MEnV0P5EdkAq4qAUlY%2bX8EX%2bX9JB%2fIsiYmPleBElADA53D%2btp6VjCxOaUEJQhp0AeKpEEUWMY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=bBrOzenpL3GnMuwrQSiBOglPfIQdmaDCq4Sah5UuexDWH1iiTsjSLWGHX57L8rLmOID0etw1l7HeNBJHTx44sBvH%2f%2bwnjUxHTM5fACxSKneYFZ0UQDhZNoibJp319U6XEeTeRJlCqbk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=HclZFE3qga42uAPfMO1NoDsZiD45MFaM5IjytpKwObqJDwBRz2E%2bFpaCljnsNFhFNtVFCxFSdEAGh4oISvROoTCFVvnnfGRfUJwkpQILGuXsTrWWDLBkkzTqG8PgLZ9uWjJvJM%2bwpeU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=9pBGRMDleULZUYyjT1IRuUImtdzdz0CO88srXtoHH%2fG9%2fIaYLOe6TTqKYfW9FAWoT4MNNORcKJVE7qPzYrHpY5o4JQBaBgo%2bBbWnJpA7hUVd1aK%2f9MBtPHT6eCdroumB6x%2b7DAU0JG4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=tV%2bJ8oxTggcOHIsn2XUvYpEJPqUxpeDvJgbTTuRnsNMeZZROmSQTQzS4nTvnArP08BRUwCWM9vaeoEY7W7wxWnpqARGbvyGgaXgSkpF29b3M7x1uo7ZJVsjPfKjJ7sJvg5mPOY7XBRU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=tgFWNn%2fkAex0PFayhU4Dtzi3vzFKPNnmki1D0law4opMURCvd5pS4LJSX8gSQSqSdzoiXyo9ztlcmPZM8ahfpas9RIrRnOiFuURpMnt8ei%2fCz7RxyU3HtfFSd7rrftU627AaGbbf5yw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=F34isCm8gnNZ6y%2fEJvbCIx4QXNzYWd4V2Yb5zJDecBPzVmgHBe6gXFP0enQ2SItt3ZJLPmFuBoxviGjCafhP6DUQsv8RuD6gYR8FCaSXW8%2boKzyuiLEb%2bO632eQlMzqkUPorvYvO2xc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=USmFtnJr1MAdiA3qxI%2bQzb75aeDyAJ%2bY%2ftVcXvx9DriimVGF0FgxmYCfTLBi55FlIp%2bzlM7uwU7dJncEP9ZZNvSg04JX4oZqA5grYIdHNbocLg7clTT97aWk1urw4CUI72mdV3m%2fVVc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=tUaYS5q9Ejcm5j3zhbGnMla94Xe%2f40KJb%2baurQcSU%2bADnZb546dAUfSTgLu3oO0fJBXfVQXZDSboiks4O4nmGraonZDRua2pEkJ6PNaHaKlnlDgsytzKTwefkZYtln9j0eGdXKkqlK4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=9OOkrTq8JyDnMIMT5ccMxVpqsEighptnmJONAZaCNqouCezMa6jB1kAdSAId%2bBFUD11JD1jdoyuD01KQSz%2bS%2bWFLmYIFOxmA1qCk%2fCF60FT%2fE3QhScpyISOFgbotG0cKZEfkXxDX0ZM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=gM6TuOgliP6jFLkK1Y0oc2IP0WxKP4RQyCyZdcjK2xRPZ6O6FH94T6xTO4WbXuw%2b53Docw040JYEPdRnQKWRbmpV8DDa%2fGTcLLL9lPwaqnONWUG5n7Jml%2f72Kids33Z%2bO0FPI1Oev9I%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=LwbSERI1xRhHuwDX8Y9p8JeAhpGrd%2bzER17z137Mg%2bJAOiyd80EGMLVlFlQmdMlrAbDq9gHhnGrIN5Ck%2bL7947UMbReSsbLIIbU8%2brEzoAO5A95Y6FBmA3M3jhZGX015XfcSWqbv2Iw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Iik3DoVO%2bsZ4QXYDSgRenwjAl7OFeJIAGmrVwHALytO3CR7Z66%2bfNju1hlu1S2xvJrMr6h6Vb4qEn%2fQteONrtWwn%2fhlc6u8qTNfsrro4MqPoxR4szG3kmuMKlS%2fTMF7kX8MWDXbz54E%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Ah4ZfFm5QuUc%2fEFqHZhhg8E71XLiTvpWF7vKx2NhAYdGEMl4c2uatVklREuqnSFgm6FGhwhpUqMANRVzSo%2frNhfCmS47VkF0nmt8Atr5ys%2f81vJocH1sJRIlKMfp1H088gYr0A8syiU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=2X6fhGHfvEOVJ98bPINVIvdCgmkBK9wyKLYzEa7l2GKTTXsNyrCpMIGsWc3BpUlLtsmp8QzDfZ2eQB7aPfsFLUi%2bMN2UrDM2Zrw2fxiCYAToEQZ68lJ%2fMpIFHviE64ES9tP5G2oOmrM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=l1AbQrqgcTbxsxCeCDV4FV9tp43ULiMv3vVGD8cLZ7R15xAA3dUoabL5gFgtf%2f5nuhjAXFNQQcwjbpt66aRR24PBm5oG1t80gaXxeAP34vVsI5bppVlVYfBirPKTpyvbV2zBh72r1iQ%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=XXEWIJYlVtGaqC0owFR7xU2j9pRexMFjjN%2ftLM%2b531hVtbKH0Hf%2fel%2fdPrmASqlIGhEQNggZOSmsB3nruldXugmCA1A9s0QkVl4IH%2fKeaNf2%2bYGiA4uJl5ZCD4Tuu7Yxd0QYEkPwG3o%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=cPYv9Bdi6IfNmqzo%2fLtp1kOvkW7Rm%2fFWZt%2fOJ4u%2fysG2O2N8LAhyXVVmrUTyHiJ43rJ4pOAte4v71SdXq8FLdetIXpzbacDt9txtI%2b9kDZ9KrATBbeMU%2bEnB8UVmse6%2fXLmXp59MtBY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=nRxIlIydGyMEGgakoZBxbFY1sVmgjU%2fnU%2fGr%2f%2bF2UGaZ9Ek628Ee3%2b0QcPi%2fekTXvBCQwq2IjW8005Kv8vbhrj99H31DLqNayl3a8hXtsM66cfIM17LH6ebDXWa8%2fszEILUO%2bYQv6oI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=rSBPZdbIREv4vJzQGZ6jsI%2fx62Sw8mFqsG1sJFyCIMDweMn%2fuGNerS9JkveZXfV2GmGhsCMZhiZd7TFh689%2bOhdVf1ucKKp%2bJpolzAAkF13H1%2b%2fZbue04oiFEbw2BZtRHc0qW3eQlsU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=4MF6qd51Akc9FQEP5ainplDEgjW8hTiQRbEYQbSNdI2VUzqSEF8EpY34gh6pEtwwrJBuPJf7sdLInAITDBbxjGwmhpT%2f6oEMIpy%2fH2dOIBbIBWr7lUIor%2f6%2bXZEwJyi5vX3yiYMCnho%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=k%2fz%2bLeUSHuE0B56hYM2YCxzxKmFvVy5c47pQl84fsdPNs3YIBnCHErtojma8AD4GRYQs7RJ9Cj%2faSnDKflhsEP0iSlZM1qtxruHmSHVLrZUgETZygEw90t9ovUxG0ykaQb3b%2fe1jSA4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=B60WyxA99P819TLAoFxHe9bdJg9N3%2br6U9cMRPHenXJ8vF15dZDWFsL0ObjmzMDjhxCJgcTaH5s51C4jUZkLpVTfGJn0BJqUkHsX%2bA0Esi2ORBDU0nzP4EUdKQaxOfUTHcHnI0rfGNc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=kTOB0J2BIUSDC0tx5B8RuP1dRM4mM7V2MU14PpwWX%2fKiW88x5Ai2V68IAb9qsQwWO8znJNcWL0%2b%2fw%2bMqxGr6BW5uZ5s%2beigp88AHUJfL%2fO22LQ8NFGTi6xUhstrOIjd8F%2bfP8WvtqBc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=y3we1vSiVWL4YBBkfB11md1TE7yoTGzhlvoMbo2S%2bOAGD8WBPDjhi8hH1e9ftGmoytn3sNUR3HoWVwmQmMMk0BvmYTLL%2bwf7nz7ClEJD2fY9LdvLvIhAgpbL4IEKH8NIN%2f16waGvQ9Q%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=dI2dxewbLKN54oqqtuzPvKt4ECpog1SFY9Jg4Vd2vuPMKXbJBItPbcocruxPCAEJLdj6gqSW6aGsbqGW%2f6QLs8wCDq5qmLLiw%2fzdD1XyfeeBmo%2bA0YIOJECkTSna841L0KrABeuwuKY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=09pD87g6ijNGpLpV4%2fgvOZob%2bLQOJv1LeNkmTlHNoL3DQCSr0JhPH0QKZY6WBrz51XwCqesMoLweTQoZ2w9904pBGDvgdemrzSdKxYacR29k1Hp7x5N3Rh3zakQAw736amActivU6JY%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=0h6Nj2X1VPVThQkTYMig%2b9P8PUpqdIueLxTwNmubiWMzmJIjEjFSc96%2fdfzAbzU8%2bK5Eo0Hkvfl81QFOW6DZ1G4AQZaw8qzPRR3btOLXX%2bQXzLEPQVHpSotOgVbkHOtqmyx1wJN77zo%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=6ysfhqeeZ4vrnwn6cjDK8sU1S9Q0t1EbNUq6B8ljnsBIYDw0wTwBVRpOatR7ggV8ZpL2ADxEhQ4sCcS2wm4xaqqVVNffBJ%2b8LwmItWTSby6l2T8BO%2fVnIyewuvT7kNNp%2b2uZdMbi6wE%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=cmBAOE7yyP1eUKcGW8zkaGOLg6%2byIWUHwXGOoa8%2fy3vpkBGe%2frtDqzgdQzrs2sCT2i12JFFKw3pGWpzdgdMCrlY6GIqbhoOSd8b6O8CFCJzaXRBg%2bSv5Sxlc6r%2b%2biMC1VTDs1l2obPQ%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=rGvX%2baMBzChJX0SMwmlrW9TqMSHeGoi9iBank1lIw1r3vlDrlAD0o9V7W18zPzLjbpAE94yC5vtEufZ7pbtL4GZ4Ul8%2f7pgLDqvohXSV%2fy5NEVLPocVAUWXOfwNYEzA%2fnu0aYXxC7Bk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=9ehtN515%2f2hv%2b5m7Aqtdrj9S4U0WImmkvGWbLM8WF0vRdN2OSgeYsOqteCzpGiCbJa6xFcCZxAyv94fyY7z9Udsu8fYMIl4zNV6Ay0%2fP3McNhmVi7usts2iSf6SQqLIWqXiYWbxan88%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=vCPd7JUGOQst%2bJm19c7GR3swrk4S8cKUniAw3aovOiSoHIX0ZJrFihyveEtJfR3vvui2ITaDs95%2fZ6USAB5Qry1Pxsy%2fI4WpFG19TfctaEguVR6I7JQ%2boNJVMzs3mwVA%2f1hq9fYKi3M%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=3DGyCStDc38Jk6VPCeYrpxYeO3cLlvx0JJBwZDrR2gbiaRk1MZJdIPE9t16T19NHOoO%2btBABPlIO8NqpuPM5tl56tCmAgERLTx8lFRg5Dkh8pEBgfUlB627q4gB53DEwdEG3fT7Nedk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Os6owwuyOLf5QLMeUBj7z6HNL%2bBxvzgr8t9M1ZUuTUgfL%2bUKs7kBLkCPpFd5Wva1uXAVpwPrnyav2puPi6TWfwHhDpi49eH76kA5YK66pXOS43kC2wYlSwI92N3k6zlJijBZQIfSk%2fo%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=NMnuqc65yURgAeADy5ovsiJBPlmi7ep8avLs6hvLnDXnqqp228tcvePQXNz0wTI3iDXUGW0OCiAlnS2ZuJ7wMDBdfJYt9X6g3582nR0vy5ZoBR%2f7gVrxPq%2byQCILmCroatfM%2beKPFf0%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=R8tWxBJfff%2bkSzRA8RweqH5yKGNtxGhRwcMNVeMbvBNp%2fqM1ckGrBI7ePUo6FMjDPgJIkwcomm1QXTHpAvD2WXdHiddCH3hxmmIQRLim9jR0ksLMyPli8t9RC7%2fJ%2f2yQ6Q9szeAX0cw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Fv8wLfTtLdmyl7zHuEsQ4qRrkg1IUW2k32u0zsSyQW6jIR5ShF7e2YFFuUqPHPB84ZGnlc2ZUYlh6pRBDQvXPmbPClxBPvQ65QDXuvArVQIZw4HqFMRh2p%2fatucNeUqoL3k8rfFYr%2b4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=gisCNl5dSTkg1IcDIZ30sRx2Aio9FiZzNmPwKqxIzIEsn2fAlv2ZaDcA0A1ob%2fGUC40w%2fQSYh5XF9TzgnYO6%2b0%2fTzkviFImuyG328eKDwbnC1DEUvDVxnI68%2bqSIyqTWA681yUKHyaU%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=SK6HwpCbSNi4cwi0LH%2f676K86BmMsAPdxbk83MRxtXm3y3DeCx7HuLYy9TXOv6f64JxvqoAbo48vC8wcR7qsddpfz2sp37zpZsGyf5XfwQy10iYlSHyATTdBLI63P1TThwH%2b%2fxM8q0E%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=GsyfL7BMU0fPpeTtDLdKL%2fwhQHTT%2fUYswFWB2pra5AFVRxjCGFDtJx0ofUSjfyAYts%2beDU2OhIvx2C66ImTkqzn3b4SzePMEksyTjFL0j3UOzaTbyHqQYpcilcensucTMA7Bx3S7WRA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=dAhJwFoiHDf968YFfjSzeh6SPYn65N%2bd89XbHS0PPjfUE5zOpEdoRhLVbd3PL6w%2fJxxn7iB6H7PJ6FZA6y1Ts8R0bYyX1y2zjMKk1vDRZengKpREWZ3lW9iiFwy9wduFz6xXGrPsQVM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=M4XVTucChiFQGOZeT1pd9Wu042vM0b0m3j1qsQ72%2b0nimKUen6WUB7a6tsL2SqtLQsS1e7sWB6YSf95gN%2ftyBHdqvDbREyaGc1sKFZw7VS6JoWLT7GnlMOD7xwm8DXNHauIkOrb9ASA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=WFg0LxrsXdiasjLXevZgN0rukRBdRHu23aYuatNWMlcxqdc0m9HB6qcU1XQ%2bNj5JS%2fdyqzsa2HkanB5B5ehW1mAytocbnDKrgqBq2orgP1B9q%2foAjAiRIGvxhHLWDQ%2bPWIJLPkUV1CI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=kZ6yTObfx7CgpEXeUUkwxnK2hfv6I5fJHYodtVIgtwMxe8LQ3aLgo8yOQEogUMcYSDriNH%2b9HiQH%2fGLeLXo2%2fWT%2fK%2bNlKgNLND8Z2VmfA59bpUuTU%2bFQDnwRp8pno9DNW7KkEuDh%2bpQ%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=7UKg02ADnIjwcLSXxDyq4c1LI321zO0zeTdNrKNa12hEzaA94Ox8FSGTbiJ37RGZ%2fNld0FRFTx0iblDn7H6gboN%2fhZLEdf5yb7%2fWfVD2ZA9zPQojMAZABH%2fb%2fVIOa8UKb2%2bNPSKg%2beg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=GfFUI5heEdkc%2fDLetcgR5mlp%2f34%2fh5wGjI6bDaj%2bW%2bq83MQoMxQQJp%2bX8eiQr4GGhV8Ivj78QqBOYrP7GhV6xXXxaNG8cRxiQAnGgwcdGIZ%2fwFuAFzTaInmS6bDx6mT89LNx1Eva3yA%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=YDxEPWP6j5d2J%2bvWQkJjR%2b5XmGl1kvGLZAMgHm%2b7Q8E2UU72muANGnKhvLKiqhv23pZ%2f%2bWJwl3xMZY0uhOCgsimxrNLAzpqG%2fF%2fM9XclJhfYGMhNbc40OT3ta%2fzWnTkPcYPU2KJeaEg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=UQ9qTVpru75rGhEvdKC0IeLk4apeWxFiUQCxUcsvjD%2b9QkdrQgf%2bl87F9CE4QkeEGK4jfih7dvbeDhA787LAgSyuTIMu0cFyt1x5qFGrZe3alq3bv0hIs3A33WuFg81ObGJ6h4Tsct4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=AAlKxSoFxzV5cWtCA37hlJoZCmBvN0No1EDnYPob7Vxk90j43WzuaAE6vbqmUtExpUjsHPaXG1tmtxhg%2bgFwENQhIY1EYYhu62AkvCBL2DXkmKzB%2bYOqX%2bMGl2qlRWo7QIjwhXrC%2b%2fI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=pU5lGZ8FxezubjtR0D2Ds9NnlnksDnbPnBU%2bPNixupZZnGhVAwVAhBwm7KXPS36rLEI5LgwCxPlqSDVwkCWciUFzDtPVGKMCaxV4rfaP8y0%2fsLK2EnLtM0mKXr%2f1uarsxOCwjLMt2cM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=XBt%2f3Ua%2b4QyDdB%2bW6PwH00eCbltWkFCNp66RVCDAWOcojn6wtePJPitH0hsU9M6SeZU%2fUSYr2FAW2fTTHUKl37OXVEl%2b7yulxSAsG6d7qFF5XM6zkx0rKBc%2bF3mY%2blFRV9IagSiDGnM%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Evj6BLOLryrOGYqPO37djZjPmbB1yvjFxqOZQmFGhQH7LwAbmjBswEaWlBd1tzb6KTPlhF2HN1Y6PI6onYCDwz0ZghUir8KuN%2br8JP5vsFwDxJyapGzfcIe0%2bRmZ5b%2bQGHZYTWXUbPI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=4mvIoX7op6COeW7kd0wK9jcwNTufvKLwhKU8BSZTzMP0edNb%2bnzyF31ygXjMY50VFSiOngkNcnJv2z2uQxqQcM2MaM3P3KWaTXJVdqqX%2fpvRLgc8stf61Y1TTLMLUi9qYCcxaKnTtFs%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=QYA6W8XsOgc8f4obJRo5rvHwSGznwnkRmJ1McwM7XQuimGlnxSJttHDZ2HJoaWRXBCwq2ftsJsWLZi5zXd9YmUTAcOJZR1I4hGGsHTEB2Xs0DN%2bbXPwLRUSpTuXuDzGo6vLjgga2jlI%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=RtsUbb5fgIFmpJUmWaGGe4JyHlwaPeInrMbIzmYZ90Nw3SzwQIZpn8wrsgk6NGdF9tM0oCaskB1AhxL83vHoy7h1kI4I%2fG5poCevFDw%2bP5HsJFlX24qjOUvcBFD9%2fhgeeZnGD3mIm2E%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=a82mgIoLNmBRQffNBYglXBcd6%2bdlNm7U7gIlDhGcw%2fcq9tL88NStgNKzvIdJGziM70m66bWAc8E3R5NuYKfu8rBS7r1nNlOqvi2f3P0rQ1Nt66ruJm9oH61RrlHm2arimSPMsK68vw4%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=2xqlYswQfobe6Dokj7IxwR3rS%2bR0xkWhG55qDgbP%2f%2fP54JjpJ3TJHClEw4tTjuu5uleWnmRpkf4T3ybA4qIHqjqGJ%2fLwafwR2iZm2MhL%2fnWbrtqjA50%2bnAgxkbWiaKM50U1wej%2bp7%2bs%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=RVhaq5BHWXQLuXoPQUHhFTJFWXTmzM2I4Ru25QHkIS2%2f%2fBSX9brwTQznB1XZC7MlAoXlegL6tEZJ6GhGR1benqT3pjOtxla1V1jdHDgmxM69cFXHABnv4fpA3LSvT0yFQ2643Eq1W%2fw%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=Zt0%2b9mAWbYGI5hTnCqfjlGd3ToBZoxVCv6OXBCyupD7sVjo8ka1NVM8cEb%2bC5hDmhI5vHndBQHF6bor3PEUuRZ1VI%2fKJbppbryJvT4Db1rhKJ9mfFSjq3CQBVlna%2bY9mTcC7Xim%2fHqc%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=jr2GKDneOe0wHS6o4FXgjlYhCXYV8MXqQptPZnwL58nqc93EQW9%2bVBEYU1NU2T4s92wPVl3Y5iyrU0xEJMDz0N0e%2b5VjOF5CjGSDMLhLgDpOSxt2%2bKbnB951aUUQe85%2b3zMkoKABt%2fk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=SxWYDisTDf%2fFrbyKdlgDQk%2bGZoZEsQTgoTdasMJsHxytrLmaWiKDc0t10HvFFYei36MSAkkTvKLups6RuGol%2fS1THznsE7poA25pP%2bq89k4jzh12MZ%2bHl3RZlUKkyaKaTCTr%2fyr18Tg%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=O%2fGa3ve8e9W%2fWcWsR2OEN3M%2bB%2bzB%2fgs%2ffZr3XWuEuxo%2b5m3NPAlhXhuYkjzL9Ljhhtt%2fo7TuU7WgNJkgyeyCvttwGpJudYRB%2baxvvfGkF8G2L90GXq%2bZ9dxqEVHZmTX3YWNAusim6Tk%3d',
    'http://microteaching.ntu.edu.tw:9002/GestaltViewer?wlGUID=%2bszYqqNVeM1%2bL7ki0SpT7s63TMuNnd51YhnWMXaGnvth%2bX6BoweFGKYA2vqDnCvLvwWsYwkLbnQs9hOI9cCj6XddQhqpEoYD5ZqsDPmQ0TsJ10EEzvNU%2fSCnrgeDPvQgzx77OeXXAv0%3d']

# Midterm microslides
cases = {
    'PA0030': {'diagnosis': 'Amyloidoma', 'organ': 'lung'},
    'PA0284': {'diagnosis': 'Chronic rejection', 'organ': 'kidney'},
    'PA0061': {'diagnosis': 'Acute cellular rejection', 'organ': 'liver'},
    # No organ specified
    'PA0264': {'diagnosis': 'Allergic rhinitis', 'organ': None},

    'PA0289': {'diagnosis': "Nephroblastoma (Wilm's tumor)", 'organ': 'kidney'},
    'PA0305': {'diagnosis': 'Neuroblastoma', 'organ': 'adrenal gland'},
    'PA0247': {'diagnosis': 'Retinoblastoma', 'organ': 'eye'},
    'PA0200': {'diagnosis': 'Hyaline membrane disease', 'organ': 'lung'},

    'PA0047': {'diagnosis': 'Squamous cell carcinoma', 'organ': 'esophagus'},
    'PA0101': {'diagnosis': 'High-grade squamous intraepithelial lesion', 'organ': 'cervix'},
    'PA0102': {'diagnosis': 'Squamous cell carcinoma', 'organ': 'uterine cervix'},
    'PA0295': {'diagnosis': 'Basal cell carcinoma', 'organ': 'skin'},
    'PA0207': {'diagnosis': 'Familial adenomatous polyposis', 'organ': 'large intestine'},
    'PA0249': {'diagnosis': 'Adenocarcinoma', 'organ': 'colon'},
    'PA0260': {'diagnosis': 'Nasopharyngeal carcinoma', 'organ': 'nasopharynx'},

    'PA0104': {'diagnosis': 'Leiomyoma', 'organ': 'uterus'},
    'PA0195': {'diagnosis': 'Neurofibroma, plexiform and diffuse', 'organ': 'soft tissue (cheek)'},
    'PA0158': {'diagnosis': 'Schwannoma', 'organ': 'soft tissue (near T-level vertebra)'},
    'PA0314': {'diagnosis': 'Hemangioma', 'organ': 'skin'},
    'PA0226': {'diagnosis': 'Embryonal rhabdomyosarcoma', 'organ': 'soft tissue'},
    'PA0100': {'diagnosis': 'Malignant melanoma', 'organ': 'vulva'},
    'PA0285': {'diagnosis': 'Mature cystic teratoma', 'organ': 'ovary'},

    # No organ specified
    'PA0170': {'diagnosis': 'Atherosclerosis', 'organ': None},
    'PA0171': {'diagnosis': 'Amyloidosis', 'organ': 'myocardium'},
    'PA0002': {'diagnosis': 'Cardiac myxoma', 'organ': 'heart, left atrium'},
    # No organ specified
    'PA0197': {'diagnosis': 'Acute rheumatic pancarditis', 'organ': None},
}

main(slides, cases)
