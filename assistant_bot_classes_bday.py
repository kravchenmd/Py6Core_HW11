from collections import UserDict
from typing import Union
from datetime import datetime
import re

EXIT_COMMANDS = ('good bye', 'close', 'exit')
PAGINATION = 2  # default number of contacts per page


# for rising custom errors in 'add_contact' function
class FieldException(Exception):
    pass


class Field:
    def __init__(self, value: str) -> None:
        self.__value = None
        self.value = value

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        self.__value = value


class Name(Field):
    def __init__(self, value: str) -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value: str) -> None:
        if value.isalpha():
            Field.value.fset(self, value)
        else:
            raise ValueError("Name must be a single alphabetic string \n" +
                             "Example: 'Abc', 'abc'")

    def get_name(self) -> str:
        return self.value


class Phone(Field):
    def __init__(self, value: str = '') -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value: str) -> None:
        pattern = r'(?:\+\d{12,13}\b)|(?:\b(?<!\+)\d{10,11}\b)|(?:\b\d{2}(?!\W)\b)'
        if re.match(pattern, value):
            Field.value.fset(self, value)
        else:
            raise ValueError("Phone must be a single numeric string\n" +
                             "Example: '+[12-13 digits]' or '[10-11 digits]'\n" +
                             "Or for DEBUG: just '[2 digits]")

    def get_phone(self) -> str:
        return self.value


class Birthday(Field):
    def __init__(self, value: str = '') -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value: str) -> None:
        try:
            Field.value.fset(self, datetime.strptime(value, "%d.%m.%Y"))
        except ValueError:
            raise ValueError("Birthday must be a single date string in format dd.mm.yyyy\n" +
                             "Example: '01.01.1970'")

    def birthday_date(self) -> str:
        date = self.value.strftime("%d.%m.%Y")
        return date

    def get_month(self) -> str:
        return self.value.month

    def get_day(self) -> str:
        return self.value.day


class Record:
    def __init__(self, name: Name) -> None:
        self.name: Name = name
        self.phone_list: list[Phone] = []
        self.birthday: Union[Birthday, None] = None

    # return f"Name '{self.name}' is already in contacts!\n" \
    #        "Try another name or change existing contact"

    def add_phone(self, phone: Phone) -> str:
        if phone.get_phone() in [phone.get_phone() for phone in self.phone_list]:
            raise FieldException("This phone number is already in the list of the contact!")
        self.phone_list.append(phone)
        return "Contact was updated successfully!"

    def get_phones(self) -> str:  # return phones in one string
        if not self.phone_list:
            return '-'
        return ', '.join([phone.get_phone() for phone in self.phone_list])

    def remove_phone(self, phone: Phone) -> str:
        if phone.get_phone() not in [el.get_phone() for el in self.phone_list]:
            return "Phone can't be removed: it's not in the list of the contact!"
        for el in self.phone_list:
            if el.get_phone() == phone.get_phone():
                self.phone_list.remove(el)
        return "Phone was removed successfully!"

    def edit_phone(self, phone: Phone, new_phone: Phone) -> str:
        if phone.get_phone() not in [el.get_phone() for el in self.phone_list]:
            return "Phone can't be changed: it's not in the list of the contact!"
        for el in self.phone_list:
            if el.get_phone() == phone.get_phone():
                self.phone_list.remove(el)
                self.phone_list.append(new_phone)
                return f"Phone number was changed successfully!"

    def add_birthday(self, birthday: Birthday) -> None:
        if self.birthday is not None:
            raise FieldException("Birthday field of this contact is already filled!")
        self.birthday = birthday

    def get_birthday(self) -> str:
        if self.birthday is None:
            return '-'
        return self.birthday.birthday_date()

    def edit_birthday(self, new_birthday: Birthday) -> str:
        if self.birthday is None:
            return "Birthday field of this contact is empty: fill it!"
        self.birthday = new_birthday
        return f"Birthday was changed successfully!"


class AddressBook(UserDict):
    def __init__(self, pagination: int = PAGINATION) -> None:
        super().__init__()
        self.pagination = pagination
        self.current_index = 0
        self.current_page = 0  # for showing page number in terminal

    def add_record(self, name: str, record: Record) -> None:
        self.data[name] = record

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_index >= len(self.data):
            self.current_index = 0
            self.current_page = 0
            raise StopIteration

        result = []

        page_end = f"\n{'--end--' : ^20}"  # at the end of the data
        for i in range(self.current_index, self.current_index + self.pagination):
            if i >= len(self.data):
                break
            name = list(self.data.keys())[i]
            result.append(f"{self.data.get(name).name.get_name()}:\t{self.data.get(name).get_phones()}" +
                          f"\t{self.data.get(name).get_birthday()}")
            self.current_index += 1
        else:
            if self.current_index < len(self.data):
                self.current_page += 1
                page_end = f"\n{'--' + str(self.current_page) + '--' : ^20}\n"  # at the end of each page

        result = '\n'.join(result) + page_end
        return result


# This decorator handles the correct number of arguments that are passed into the function
def func_arg_error(func):
    def wrapper(*args):
        try:
            result = func(*args)
            return result
        except TypeError:
            f_name = func.__name__
            if f_name in ('exit_program', 'hello', 'show_all_phones'):
                return "ERROR: This command has to be written without arguments!"
            if f_name in ('show_phone', 'days_to_birthday'):
                return "ERROR: This command needs 1 arguments: 'name' separated by 1 space!"
            if f_name in ('add_contact',):
                return "ERROR: This command needs 1 obligatory argument 'name' and 2 supplementary " \
                        "'phone' and 'birthday' separated by 1 space!"
            if f_name in ('edit_birthday',):
                return "ERROR: This command needs 2 arguments: 'name' and 'birthday' separated by 1 space!"
            if f_name in ('remove_phone',):
                return "ERROR: This command needs 2 arguments: 'name' and 'phone' separated by 1 space!"
            if f_name in ('edit_phone',):
                return "ERROR: This command needs 3 arguments: 'name', 'phone' and 'new_phone' separated by 1 space!"
            return "Some unhandled error occurred!"

    return wrapper


@func_arg_error
def hello() -> str:
    return "Hello! How can I help you?"


@func_arg_error
def add_contact(contacts: AddressBook, name: str, phone: str = '', birthday: str = '') -> str:

    try:
        n = Name(name)
        p = Phone(phone) if phone else None
        b = Birthday(birthday) if birthday else None
    except ValueError as err:
        return f"ERROR: {err}"

    if name in contacts.data.keys():
        if not phone and not birthday:
            return "ERROR: The name itself of the contact is already created! Try to update it!"
        if phone:
            try:
                contacts.data[name].add_phone(p)
            except FieldException as msg:
                return str(msg)
        if birthday:
            try:
                contacts.data[name].add_birthday(b)
            except FieldException as msg:
                return str(msg)
        return "Contact was updated successfully!"
    else:
        contact_record = Record(n)
        if phone:
            contact_record.add_phone(p)
        if birthday:
            contact_record.add_birthday(b)
        contacts.add_record(name, contact_record)
        return f"Contact was created successfully!"


@func_arg_error
def edit_phone(contacts: AddressBook, name: str, phone: str, new_phone: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    try:
        p = Phone(phone)
        new_p = Phone(new_phone)
    except ValueError as err:
        return f"ERROR: {err}"

    result = contacts.data.get(name).edit_phone(p, new_p)
    return result


@func_arg_error
def edit_birthday(contacts: AddressBook, name: str, new_birthday: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    try:
        b = Birthday(new_birthday)
    except ValueError as err:
        return f"ERROR: {err}"

    result = contacts.data.get(name).edit_birthday(b)
    return result


@func_arg_error
def remove_phone(contacts: AddressBook, name: str, phone: str) -> str:
    """
    Remove phone number from the contact. But doesn't remove contact itself if it has no phone numbers.
    """
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    try:
        p = Phone(phone)
    except ValueError as err:
        return f"ERROR: {err}"
    result = contacts.data.get(name).remove_phone(p)
    return result


@func_arg_error
def show_phone(contacts: AddressBook, name: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    return contacts.get(name).get_phones()


@func_arg_error
def show_all_phones(contacts: AddressBook) -> str:
    if not contacts.data:
        return "There are no contacts to show yet..."
    result = ''
    for page in contacts:
        result += page
    return result


@func_arg_error
def days_to_birthday(contacts: AddressBook, name: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    if contacts[name].birthday is None:
        return "This contact has no birthday field!"
    now = datetime.now()
    birthday = datetime(now.year, contacts[name].birthday.get_month(), contacts[name].birthday.get_day())
    if birthday < now:
        birthday = birthday.replace(year=now.year + 1)
    days = (birthday - now).days + 1
    return f"{days} day(s) to {contacts[name].name.get_name()}'s birthday!"


@func_arg_error
def exit_program():
    return "Good bye!"


def choose_command(cmd: str) -> tuple:
    if cmd in EXIT_COMMANDS:
        return exit_program, []

    cmd = parse_command(cmd)
    cmd_check = cmd[0].lower()
    if cmd_check == 'hello':
        return hello, cmd[1:]
    if cmd_check == 'add':
        return add_contact, cmd[1:]
    if cmd_check == 'change':
        return edit_phone, cmd[1:]
    if cmd_check == 'remove':
        return remove_phone, cmd[1:]
    if cmd_check == 'phone':
        return show_phone, cmd[1:]
    if cmd_check == 'show' and len(cmd) > 1:
        # take into account that this command consists 2 words
        cmd_check = cmd[1].lower()
        if cmd_check == 'all':
            return show_all_phones, []
    if cmd_check == 'edit' and len(cmd) > 1:
        # take into account that this command consists 2 words
        cmd_check = cmd[1].lower()
        if cmd_check == 'birthday':
            return edit_birthday, cmd[2:]
    if cmd_check == 'days_to_birthday':
        return days_to_birthday, cmd[1:]
    return None, "Unknown command!"


def parse_command(cmd: str) -> list:
    return cmd.strip().split(' ')  # apply strip() as well to exclude spaces at the ends


def handle_cmd(cmd: str, contacts: AddressBook) -> tuple:
    func, result = choose_command(cmd)
    if func:
        # else part to take into account hello() and show()
        args = [contacts] + result if func not in (hello, exit_program) else result
        result = func(*args)
    return func, result


def main():
    # create address book (UserDict)
    contacts = AddressBook()  # AddressBook(pagination_size)

    while True:
        command = None
        # Check if command is not empty
        while not command:
            command = input('Enter command: ')

        func, result = handle_cmd(command, contacts)
        print(result)

        if func == exit_program:
            break
        print()


if __name__ == '__main__':
    main()
