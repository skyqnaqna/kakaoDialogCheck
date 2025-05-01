import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict
import re
from datetime import datetime, timedelta

def check_authentication_from_file(file_path, keywords, duration, isDurationFixed, is_pc_selected):
    auth_count = defaultdict(int)
    already_authenticated = defaultdict(set)

    today = datetime.now()
    todayMidnight = today.replace(hour=23, minute=59, second=59, microsecond=0)

    if not duration:
      one_week_ago = todayMidnight
    else:
      one_week_ago = todayMidnight - timedelta(days=duration)

    endDate = todayMidnight.strftime("%m.%d")

    if isDurationFixed:
      monday = todayMidnight - timedelta(days = todayMidnight.weekday())
      if monday != todayMidnight:
        monday = monday.replace(hour=23, minute=59, second=59, microsecond=0)
      one_week_ago = monday - timedelta(days=7)
      endDate = monday.strftime("%m.%d")

    startDate = (one_week_ago + timedelta(days = 1)).strftime("%m.%d")
    date_text.delete(1.0, tk.END)
    date_text.insert(tk.CURRENT,f"인증 기간: {startDate}~{endDate}\n")


    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()
        if is_pc_selected == False:
          for line in content:
            date_match = re.match(r'(\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.\s*([오후|오전]+)\s*(\d{1,2}):(\d{2})),\s*(.*?):\s*(.*)', line)

            if date_match:
              date_str = date_match.group(1).strip()
              user = date_match.group(5).strip()
              message = date_match.group(6).strip()
              date_str = date_str.replace("오후","PM")
              date_str = date_str.replace("오전","AM")

              try:
                message_date = datetime.strptime(date_str, '%Y. %m. %d. %p %H:%M')
                if isDurationFixed:
                  if monday >= message_date >= one_week_ago:
                    date_key = message_date.strftime('%Y-%m-%d')
                    if date_key not in already_authenticated[user]:
                      for keyword in keywords:
                        if keyword in message:
                          auth_count[user] += 1
                          already_authenticated[user].add(date_key)
                          break
                else:
                  if message_date >= one_week_ago:
                    date_key = message_date.strftime('%Y-%m-%d')
                    if date_key not in already_authenticated[user]:
                      for keyword in keywords:
                        if keyword in message:
                          auth_count[user] += 1
                          already_authenticated[user].add(date_key)
                          break
              except ValueError:
                continue

        else:
          print("is_pc_selected", is_pc_selected)
          for line in content:
            splited = line.split(",")

            if len(splited)>=3:
              date_str = splited[0]
              user = splited[1]
              message = splited[2]
              try:
                message_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                if isDurationFixed:
                  if monday >= message_date >= one_week_ago:
                    date_key = message_date.strftime('%Y-%m-%d')
                    if date_key not in already_authenticated[user]:
                      for keyword in keywords:
                        if keyword in message:
                          auth_count[user] += 1
                          already_authenticated[user].add(date_key)
                          break
                else:
                  if message_date >= one_week_ago:
                    date_key = message_date.strftime('%Y-%m-%d')
                    if date_key not in already_authenticated[user]:
                      for keyword in keywords:
                        if keyword in message:
                          auth_count[user] += 1
                          already_authenticated[user].add(date_key)
                          break
              except ValueError:
                continue

    except Exception as e:
      messagebox.showerror("Error", str(e))
      return None
    return (auth_count, already_authenticated)

def load_file():
  file_path = filedialog.askopenfilename(title="Select text file", filetypes=[('csv files',"*.csv")])
  keywords_input = keyword_entry.get().strip()
  duration = duration_entry.get()

  if not keywords_input:
    messagebox.showwarning("Input Required", "인증할 키워드를 입력해 주세요.")
    return

  if not duration and date_selection.get() == "custom":
    messagebox.showwarning("Input Required", "기간을 입력해 주세요.")
    return

  if date_selection.get() == "custom":
    try:
      duration = int(duration)
    except:
      messagebox.showwarning("Input Required", "기간에 숫자만 입력해 주세요")
      return

  keywords = [keyword.strip() for keyword in keywords_input.split(",")]
  print(is_pc_selected.get())
  if file_path:

    if date_selection.get() == "fixed":
      result = check_authentication_from_file(file_path, keywords, duration, True, is_pc_selected.get())
    else:
      result = check_authentication_from_file(file_path, keywords, duration, False, is_pc_selected.get())
    if result[0] is not None:
      output_text.delete(1.0, tk.END)
      if result[0]:
        for user, count in result[0].items():
          for inner_user, timestamps in result[1].items():
            if inner_user == user:
              output_text.insert(tk.END, f"{user}: {count}회 인증\n{timestamps}\n")
      else:
        output_text.insert(tk.END, "인증할 내용이 없습니다.")


root = tk.Tk()
root.title("운동 인증 체크 앱")
root.geometry("400x600")


keyword_frame = tk.Frame(root)
keyword_frame.pack(pady=10)

keyword_label = tk.Label(keyword_frame, text="인증 키워드 입력 (쉼표로 구분):")
keyword_label.pack(side=tk.LEFT)

keyword_entry = tk.Entry(keyword_frame, width=30)
keyword_entry.insert(-1, '오운완')
keyword_entry.pack(side=tk.LEFT)

date_selection = tk.StringVar(value="fixed")

fixed_period_button = tk.Radiobutton(root, text="고정 기간 (지난주 화~이번주 월)", variable=date_selection, value="fixed")
fixed_period_button.pack(anchor=tk.W)

custom_period_button = tk.Radiobutton(root, text="사용자 정의 기간", variable=date_selection, value="custom")
custom_period_button.pack(anchor=tk.W)

duration_frame = tk.Frame(root)
duration_frame.pack(pady=10)

duration_label = tk.Label(duration_frame, text="기간 입력 (단위는 일):")
duration_label.pack(side=tk.LEFT)

date_text = tk.Text(root, height=1, width=30)
date_text.pack(pady=10)

duration_entry = tk.Entry(duration_frame, width=30)
duration_entry.pack(side=tk.LEFT)

is_pc_selected = tk.BooleanVar(value=True)

pc_button = tk.Radiobutton(root, text="PC", variable=is_pc_selected, value=True)
mobile_button = tk.Radiobutton(root, text="Mobile", variable=is_pc_selected, value=False)

pc_button.pack(anchor=tk.W)
mobile_button.pack(anchor=tk.W)

load_button = tk.Button(root, text="텍스트 파일 열기", command=load_file)
load_button.pack(pady=10)

output_text = tk.Text(root, height=25, width=50)
output_text.pack(pady=10)

root.mainloop()



