class Tools:

    @staticmethod
    def create_link_to_emp(emp):
        '''
        Создание ссылки на юзера
        '''
        emp_url = f'tg://user?id={emp.id}'
        emp_html = f"<a href=\"{emp_url}\">{emp.fio}</a>"
        return emp_html

    @staticmethod
    def form_list_participants(participants, index=0):
        '''
        Формирование текстового спика поздравляющих или его части(если длина слишком большая)
        '''
        text = ""
        for i in range(index, len(participants)):
            if len(text) >= 3500:
                return (text, i)
            text += f"{i + 1}. {Tools.create_link_to_emp(participants[i].employee)}\n"

        return (text, None)

    @staticmethod
    def form_list_wishes(wishes, index=0):
        '''
        Формирование текстового спика желаний или его части(если длина слишком большая)
        '''
        text = ""
        for i in range(index, len(wishes)):
            if len(text) >= 3500:
                return (text, i)
            text += f"{i + 1}. {wishes[i].text}\n"

        return (text, None)
