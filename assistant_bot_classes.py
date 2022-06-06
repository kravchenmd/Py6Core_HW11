from collections import UserDict
from typing import List

EXIT_COMMANDS = ('good bye', 'close', 'exit')


class Field:
    pass


class Name(Field):
    def __init__(self, name: str) -> None:
        self.name = name

    def get_name(self) -> str:
        return self.name


class Phone(Field):
    def __init__(self, phone: str = '') -> None:
        self.phone = phone

    def get_phone(self) -> str:
        return self.phone


class Record:
    def __init__(self, name: Name) -> None:
        self.name: Name = name
        self.phone_list: List[Phone] = []

    def add_phone(self, phone: Phone) -> str:
        if phone in self.phone_list:
            return f"Name '{self.name}' is already in contacts!\n" \
                   "Try another name or change existing contact"
        self.phone_list.append(phone)
        return "Phone was added successfully!"

    def get_phones(self) -> str:  # return phones in one string
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


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()

    def add_record(self, name: str, record: Record) -> None:
        self.data[name] = record


# This decorator handles correctness of the phone number: can start with '+'
# and then must contain only digits. But doesn't check if the number is real
def input_error(func):
    def wrapper(*args):
        if len(args) not in (3, 4):
            return func(*args)

        name, *phone = args[1:]
        try:
            for el in phone:
                phone_check = el[1:] if el.startswith('+') else el
                # check at once if the phone number doesn't start with '-' sign
                # and if it contains only digits by int()
                if int(phone_check) < 0:
                    raise ValueError
        except ValueError:
            return "ERROR: Phone can or couldn't start with '+' and then must contain only digits!\n" \
                   "Example: +380..., 380..."

        result = func(*args)
        return result

    return wrapper


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
            if f_name == 'show_phone':
                return "ERROR: This command needs 1 arguments: 'name' separated by 1 space!"
            if f_name in ('add_contact', 'remove_phone'):
                return "ERROR: This command needs 2 arguments: 'name' and 'phone' separated by 1 space!"
            if f_name in ('edit_phone',):
                return "ERROR: This command needs 3 arguments: 'name', 'phone' and 'new_phone' separated by 1 space!"

    return wrapper


@func_arg_error
def hello() -> str:
    return "Hello! How can I help you?"


@input_error
@func_arg_error
def add_contact(contacts: AddressBook, name: str, phone: str) -> str:
    n = Name(name)
    p = Phone(phone)

    if name in contacts.data.keys():
        contacts.data[name].add_phone(p)
        return f"Phone number was added successfully to the existed contact {name}!"

    contact_record = Record(n)
    contact_record.add_phone(p)
    contacts.add_record(name, contact_record)
    return f"Contact was created successfully!"


@input_error
@func_arg_error
def edit_phone(contacts: AddressBook, name: str, phone: str, new_phone: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    p = Phone(phone)
    new_p = Phone(new_phone)
    result = contacts.data.get(name).edit_phone(p, new_p)
    return result


@input_error
@func_arg_error
def remove_phone(contacts: AddressBook, name: str, phone: str) -> str:
    """
    Remove phone number from the contact. But doesn't remove contact itself if it has no phone numbers.
    """
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    p = Phone(phone)
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

    result = []
    for _, record in contacts.data.items():
        result.append(f"{record.name.get_name()}: " + record.get_phones())
    return '\n'.join(result)


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
    if cmd_check == 'show':
        # take into account that this command consists 2 words
        cmd_check = cmd[1].lower()
        if cmd_check == 'all':
            return show_all_phones, []
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
    contacts = AddressBook()

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
