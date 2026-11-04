# ==========================================================
#  PROJECT: LibraSentinel - A Library Borrowing and Tracking System
#  COURSE:  ITE 260 - Computer Programming 1
#  SCHOOL:  PHINMA - Cagayan de Oro College
#  DATE:    September 18, 2026
# ==========================================================
import re
from datetime import date, timedelta

# ---------------------- CONSTANTS -------------------------
LOAN_DAYS = 7        # how many days a book can be borrowed
MAX_LOANS = 3        # max books one borrower can hold at once
DATE_FORMAT = "%b %d, %Y"   # example: Sep 18, 2026

# Subjects a book can belong to (a book's Category is its subject).
# To support another subject later, just add its name to this list.
SUBJECTS = ["Introduction to Computing", "Computer Programming 1"]

# ID formats (must match Section XI: Data Format Standards in the paper)
BOOK_ID_PATTERN = r"B\d{3}"                 # B + 3 digits           -> B001
BOOK_ID_EXAMPLE = "B001"
STUDENT_ID_PATTERN = r"\d{2}-\d{4}-\d{6}"   # 2-4-6 digits           -> 02-2627-010147
STUDENT_ID_EXAMPLE = "02-2627-010147"
SECTION_PATTERN = r"[A-Z]{2}\d-[A-Z]+-\d{2}"  # CAPITAL letters only -> FB1-BSIT-03
SECTION_EXAMPLE = "FB1-BSIT-03"

# Author names: letters and single spaces only (no numbers or symbols)
AUTHOR_PATTERN = r"[A-Za-z]+( [A-Za-z]+)*"

# Reminder shown before Librarian actions
BACK_HINT = "(Press ENTER to go back to the previous menu.)"

# ---------------------- DATA STORAGE ----------------------
# Lists that store system data in memory
# [book_id, title, author, category (= subject), status]
# SAMPLE BOOKS: starter records so each subject has books to borrow.
# Edit them, remove them, or empty this list ( books = [] ) if not wanted.
books = [
    ["B001", "Discovering Computers", "Misty E. Vermaat",
     "Introduction to Computing", "Available"],
    ["B002", "Computer Science: An Overview", "J. Glenn Brookshear",
     "Introduction to Computing", "Available"],
    ["B003", "Computing Essentials", "Timothy J. O'Leary",
     "Introduction to Computing", "Available"],
    ["B004", "Python Crash Course", "Eric Matthes",
     "Computer Programming 1", "Available"],
    ["B005", "Automate the Boring Stuff with Python", "Al Sweigart",
     "Computer Programming 1", "Available"],
    ["B006", "Think Python", "Allen B. Downey",
     "Computer Programming 1", "Available"],
]
students = []       # [student_id, section]
transactions = []   # [trans_id, book_id, student_id, date_borrowed, due_date, date_returned]

# Librarian accounts: [username, password]  (add more accounts here if needed)
librarian_accounts = [
    ["staff", "staff123"],
]

# Index names so the code is easier to read than book[3], trans[5], etc.
B_ID, B_TITLE, B_AUTHOR, B_CATEGORY, B_STATUS = 0, 1, 2, 3, 4
U_ID, U_SECTION = 0, 1
T_ID, T_BOOK, T_BORROWER, T_BORROWED, T_DUE, T_RETURNED = 0, 1, 2, 3, 4, 5


# ==========================================================
#  PART 1: DATA / LOGIC FUNCTIONS (no input(), no menus)
#  These take parameters and RETURN results.
# ==========================================================
def find_book(book_id):
    """Return the book record with this ID, or None if not found."""
    for book in books:
        if book[B_ID] == book_id:
            return book
    return None


def find_borrower(student_id):
    """Return the student record with this ID, or None if not found."""
    for person in students:
        if person[U_ID] == student_id:
            return person
    return None


def count_active_loans(borrower_id):
    """Count how many books this borrower has not yet returned."""
    count = 0
    for trans in transactions:
        if trans[T_BORROWER] == borrower_id and trans[T_RETURNED] is None:
            count += 1
    return count


def add_book(book_id, title, author, category):
    """Register a new book. Returns (success, message)."""
    if find_book(book_id) is not None:
        return False, f"Book ID {book_id} already exists!"
    books.append([book_id, title, author, category, "Available"])
    return True, f"Book added: '{title}' by {author} (ID: {book_id})"


def edit_book(book_id, new_title, new_author, new_category):
    """Update a book's details. A blank value keeps the old one."""
    book = find_book(book_id)
    if book is None:
        return False, f"Book ID {book_id} not found."
    if new_title != "":
        book[B_TITLE] = new_title
    if new_author != "":
        book[B_AUTHOR] = new_author
    if new_category != "":
        book[B_CATEGORY] = new_category
    return True, f"Book {book_id} updated."


def remove_book(book_id):
    """Delete a book from the system. A borrowed book cannot be removed."""
    book = find_book(book_id)
    if book is None:
        return False, f"Book ID {book_id} not found."
    if book[B_STATUS] == "Borrowed":
        return False, f"Book ID {book_id} is currently borrowed and cannot be removed."
    books.remove(book)
    return True, f"Book {book_id} ('{book[B_TITLE]}') removed."


def get_available_books():
    """Return only the books that are currently Available."""
    available = []
    for book in books:
        if book[B_STATUS] == "Available":
            available.append(book)
    return available


def get_available_books_by_subject(subject):
    """Return only the Available books that belong to the given subject."""
    matches = []
    for book in get_available_books():
        if book[B_CATEGORY].lower() == subject.lower():
            matches.append(book)
    return matches


def get_books_by_subject(subject):
    """Return ALL books (any status) that belong to the given subject."""
    matches = []
    for book in books:
        if book[B_CATEGORY].lower() == subject.lower():
            matches.append(book)
    return matches


def search_books(keyword):
    """Return a list of books whose ID, title, author, or category match."""
    keyword = keyword.lower()
    results = []
    for book in books:
        if (keyword in book[B_ID].lower()
                or keyword in book[B_TITLE].lower()
                or keyword in book[B_AUTHOR].lower()
                or keyword in book[B_CATEGORY].lower()):
            results.append(book)
    return results


def sort_books(field_index):
    """Return a sorted COPY of the books list by the given field index."""
    # key=lambda tells sorted() which item of each record to compare
    return sorted(books, key=lambda book: book[field_index].lower())


def register_student(student_id, section):
    """Register a student. Returns (success, message)."""
    if find_borrower(student_id) is not None:
        return False, f"Student ID {student_id} is already registered."
    students.append([student_id, section])
    return True, f"Registered student {student_id} (Section: {section}). You may now log in."


def login_student(student_id, section):
    """Return True only if the ID and Section match a registered student."""
    student = find_borrower(student_id)
    if student is None:
        return False
    return student[U_SECTION] == section      # exact, case-sensitive match


def login_librarian(username, password):
    """Return True only if the username and password match a librarian account."""
    for account in librarian_accounts:
        if account[0] == username and account[1] == password:
            return True
    return False


def borrow_book(book_id, borrower_id, today):
    """Process a borrowing. Returns (success, message)."""
    book = find_book(book_id)
    if book is None:
        return False, f"Book ID {book_id} not found in system."
    if find_borrower(borrower_id) is None:
        return False, f"Student ID {borrower_id} is not registered."
    if book[B_STATUS] != "Available":
        return False, f"Book ID {book_id} is currently borrowed."
    if count_active_loans(borrower_id) >= MAX_LOANS:
        return False, f"Student {borrower_id} already has {MAX_LOANS} books (limit reached)."

    due_date = today + timedelta(days=LOAN_DAYS)      # arithmetic on dates
    book[B_STATUS] = "Borrowed"
    transactions.append([len(transactions) + 1, book_id, borrower_id,
                         today, due_date, None])
    return True, (f"Book '{book[B_TITLE]}' borrowed by {borrower_id}. "
                  f"Due: {due_date.strftime(DATE_FORMAT)}")


def return_book(book_id, today):
    """Process a return. Returns (success, message)."""
    book = find_book(book_id)
    if book is None:
        return False, f"Book ID {book_id} not found."
    if book[B_STATUS] != "Borrowed":
        return False, f"Book ID {book_id} is not borrowed."

    for trans in transactions:
        if trans[T_BOOK] == book_id and trans[T_RETURNED] is None:
            trans[T_RETURNED] = today
            book[B_STATUS] = "Available"
            days_late = (today - trans[T_DUE]).days    # arithmetic on dates
            if days_late > 0:
                return True, f"Book {book_id} returned {days_late} day(s) LATE. Now Available."
            return True, f"Book {book_id} returned on time. Now Available."

    # Status said "Borrowed" but no open transaction exists (data mismatch)
    return False, f"No open borrowing record found for Book ID {book_id}."


def get_active_loans():
    """Return all transactions that have not been returned yet."""
    active = []
    for trans in transactions:
        if trans[T_RETURNED] is None:
            active.append(trans)
    return active


def get_returned_loans():
    """Return all transactions that have already been returned."""
    returned = []
    for trans in transactions:
        if trans[T_RETURNED] is not None:
            returned.append(trans)
    return returned


def get_student_loans(student_id):
    """Return the active transactions that belong to one student."""
    mine = []
    for trans in get_active_loans():
        if trans[T_BORROWER] == student_id:
            mine.append(trans)
    return mine


def get_overdue_loans(today):
    """Return active transactions whose due date has already passed."""
    overdue = []
    for trans in get_active_loans():
        if trans[T_DUE] < today:
            overdue.append(trans)
    return overdue


# ==========================================================
#  PART 2: INPUT HELPERS (validation)
#  Every helper keeps asking until the input is valid, and
#  shows an "Error: ..." message each time it is not.
#
#  BACK / CANCEL: helpers called with allow_back=True return
#  None when the user just presses ENTER. The menu action then
#  returns to the previous menu (nothing is changed).
# ==========================================================
def read_text(prompt, allow_back=False):
    """Keep asking until the user types something that is not blank.
    If allow_back is True, a blank entry returns None (= go back)."""
    while True:
        value = input(prompt).strip()
        if value != "":
            return value
        if allow_back:
            return None
        print("Error: This field cannot be empty. Please try again.")


def read_id(prompt, pattern, example, label="ID", allow_back=False):
    """Read an ID that matches the required format, converted to UPPERCASE."""
    while True:
        value = read_text(prompt, allow_back)
        if value is None:
            return None
        value = value.upper()
        if re.fullmatch(pattern, value):
            return value
        print(f"Error: Invalid {label}. Please try again.")
        print(f"       Correct format example: {example}")


def read_exact(prompt, pattern, example, label):
    """Read a value that must match the format EXACTLY (no auto-changing)."""
    while True:
        value = read_text(prompt)
        if re.fullmatch(pattern, value):
            return value
        print(f"Error: Invalid {label}. Please try again.")
        print(f"       Correct format example: {example}")


def read_book_id(prompt, allow_back=False):
    """Read a Book ID in the format B001."""
    return read_id(prompt, BOOK_ID_PATTERN, BOOK_ID_EXAMPLE, "Book ID", allow_back)


def read_student_id(prompt, allow_back=False):
    """Read a Student ID exactly as 02-2627-010147."""
    if allow_back:
        return read_id(prompt, STUDENT_ID_PATTERN, STUDENT_ID_EXAMPLE,
                       "Student ID", True)
    return read_exact(prompt, STUDENT_ID_PATTERN, STUDENT_ID_EXAMPLE, "Student ID")


def read_section(prompt):
    """Read a Section exactly as FB1-BSIT-03 (capital letters required)."""
    return read_exact(prompt, SECTION_PATTERN, SECTION_EXAMPLE, "Section")


def read_author(prompt, allow_blank=False, allow_back=False):
    """Read an author name: letters and spaces only (no numbers/symbols).
    allow_blank=True: a blank entry returns "" (used by Edit Book to keep the old value).
    allow_back=True:  a blank entry returns None (used by Add Book to go back)."""
    while True:
        value = input(prompt).strip()
        if value == "":
            if allow_blank:
                return ""
            if allow_back:
                return None
            print("Error: This field cannot be empty. Please try again.")
        elif re.fullmatch(AUTHOR_PATTERN, value):
            return value
        else:
            print("Error: Author name must contain letters only. Please try again.")


def read_number(prompt, low, high, error_message):
    """Read a whole number from low to high (inclusive), or show error_message."""
    while True:
        choice = input(prompt).strip()
        if choice.isdecimal() and low <= int(choice) <= high:
            return int(choice)
        print(error_message)


def read_menu_choice(low, high):
    """Read a menu option number between low and high (inclusive)."""
    return read_number(f"Enter your choice ({low}-{high}): ", low, high,
                       "Error: Invalid option. Please select a valid option.")


def read_selection(prompt, low, high):
    """Read a selection from a list (subject, book, ...)."""
    return read_number(prompt, low, high,
                       "Error: Invalid selection. Please try again.")


def ask_yes_no(prompt):
    """Ask a y/n question. Returns True for yes."""
    while True:
        answer = input(prompt).strip().lower()
        if answer == "y":
            return True
        if answer == "n":
            return False
        print("Error: Invalid input. Please type y or n.")


def ask_retry():
    """Ask the user if they want to try again. Returns True for yes."""
    return ask_yes_no("Try again? (y/n): ")


def repeat_until_done(action):
    """Run a menu action again after an error, until it works or the user stops.
    The action must return True when finished and False when an error happened."""
    while True:
        if action():
            return
        if not ask_retry():
            return


def go_back():
    """Tell the user the action was cancelled. Returns True (= finished, no retry)."""
    print("\nCancelled. Returning to the previous menu.")
    return True


def fit(text, width):
    """Cut text so long values do not break the table columns."""
    text = str(text)
    if len(text) > width:
        return text[:width - 2] + ".."
    return text


# ==========================================================
#  PART 3: DISPLAY FUNCTIONS (printing only)
#  Every record view uses the same table format.
# ==========================================================
def print_table(heading, headers, widths, rows, empty_message):
    """Print any list of rows as a neat table."""
    total = sum(widths) + 3 * (len(widths) - 1)    # 3 = width of " | "
    line = "=" * total
    print("\n" + line)
    print(heading)
    print(line)
    print(" | ".join(f"{h:<{w}}" for h, w in zip(headers, widths)))
    print("-" * total)
    if not rows:
        print(empty_message)
    for row in rows:
        print(" | ".join(f"{fit(cell, w):<{w}}" for cell, w in zip(row, widths)))
    print(line)
    print(f"Total records: {len(rows)}")


def show_books(book_list, heading):
    """Print a table of books."""
    rows = []
    for book in book_list:
        rows.append([book[B_ID], book[B_TITLE], book[B_AUTHOR],
                     book[B_CATEGORY], book[B_STATUS]])
    print_table(heading,
                ["BOOK ID", "BOOK TITLE", "AUTHOR", "CATEGORY", "STATUS"],
                [10, 28, 20, 25, 9], rows, "No books to show.")


def show_borrowers():
    """Print all registered students."""
    rows = []
    for person in students:
        rows.append([person[U_ID], person[U_SECTION],
                     count_active_loans(person[U_ID])])
    print_table("REGISTERED STUDENTS",
                ["STUDENT ID", "SECTION", "BOOKS HELD"],
                [16, 14, 10], rows, "No students registered yet.")


def show_transactions(trans_list, heading):
    """Print a table of transactions."""
    rows = []
    for t in trans_list:
        returned = t[T_RETURNED].strftime(DATE_FORMAT) if t[T_RETURNED] else "Not yet"
        rows.append([t[T_ID], t[T_BOOK], t[T_BORROWER],
                     t[T_BORROWED].strftime(DATE_FORMAT),
                     t[T_DUE].strftime(DATE_FORMAT), returned])
    print_table(heading,
                ["#", "BOOK ID", "BORROWER", "BORROWED", "DUE", "RETURNED"],
                [4, 10, 16, 12, 12, 12], rows, "No records to show.")


def show_overdue_notices(overdue_list, today):
    """Print a table of overdue books with days late."""
    rows = []
    for t in overdue_list:
        book = find_book(t[T_BOOK])
        title = book[B_TITLE] if book else "Unknown"
        rows.append([t[T_BOOK], title, t[T_BORROWER],
                     t[T_DUE].strftime(DATE_FORMAT), (today - t[T_DUE]).days])
    print_table("OVERDUE BOOKS",
                ["BOOK ID", "BOOK TITLE", "BORROWER", "DUE", "DAYS LATE"],
                [10, 26, 16, 12, 9], rows, "No overdue books. Great!")


def print_result(result):
    """Print a (success, message) pair. Returns True if it was a success."""
    success, message = result
    if success:
        print(f"\n[SUCCESS] {message}")
    else:
        print(f"\nError: {message}")
    return success


# ==========================================================
#  PART 4: MENU ACTIONS (mix input + logic + display)
#  Actions that can fail return True (done) or False (error),
#  so the menu can offer "Try again?".
# ==========================================================
# ---------- Shared actions ----------
def menu_search_book():
    """Pick a subject, then show ALL books under that subject in a table."""
    print("\nSelect Subject:\n")
    print_subject_list()
    print("[0] Back")
    choice = read_selection(f"Enter subject number (0-{len(SUBJECTS)}): ",
                            0, len(SUBJECTS))
    if choice == 0:
        return
    subject = SUBJECTS[choice - 1]
    show_books(get_books_by_subject(subject), f"BOOKS UNDER {subject.upper()}")


def menu_sort_books():
    print("\nSort by: [1] Title  [2] Author  [3] Category  [4] Availability")
    choice = read_selection("Enter your choice (1-4): ", 1, 4)
    field = {1: B_TITLE, 2: B_AUTHOR, 3: B_CATEGORY, 4: B_STATUS}[choice]
    show_books(sort_books(field), "BOOKS (SORTED)")


# ---------- Subject choosing (used by Add Book / Edit Book) ----------
def print_subject_list():
    for number, subject in enumerate(SUBJECTS, start=1):
        print(f"[{number}] {subject}")


def read_subject(allow_back=False):
    """Ask the user to pick one subject from the list. Returns its name.
    If allow_back is True, [0] Back is shown and returns None."""
    print("\nSelect the subject of the book:")
    print_subject_list()
    if allow_back:
        print("[0] Back")
        choice = read_selection(f"Enter subject number (0-{len(SUBJECTS)}): ",
                                0, len(SUBJECTS))
        if choice == 0:
            return None
        return SUBJECTS[choice - 1]
    choice = read_selection(f"Enter subject number (1-{len(SUBJECTS)}): ",
                            1, len(SUBJECTS))
    return SUBJECTS[choice - 1]


def read_optional_subject():
    """Like read_subject, but a blank entry keeps the current subject ("")."""
    print("\nSelect the new subject (leave blank to keep the current one):")
    print_subject_list()
    while True:
        value = input(f"Enter subject number (1-{len(SUBJECTS)}): ").strip()
        if value == "":
            return ""
        if value.isdecimal() and 1 <= int(value) <= len(SUBJECTS):
            return SUBJECTS[int(value) - 1]
        print("Error: Invalid selection. Please try again.")


# ---------- Librarian actions ----------
def menu_add_book():
    print(BACK_HINT)
    book_id = read_book_id(f"Enter Book ID (e.g., {BOOK_ID_EXAMPLE}): ", allow_back=True)
    if book_id is None:
        return go_back()
    title = read_text("Enter Book Title: ", allow_back=True)
    if title is None:
        return go_back()
    author = read_author("Enter Author: ", allow_back=True)
    if author is None:
        return go_back()
    category = read_subject(allow_back=True)
    if category is None:
        return go_back()
    return print_result(add_book(book_id, title, author, category))


def menu_edit_book():
    print(BACK_HINT)
    book_id = read_book_id("Enter Book ID to edit: ", allow_back=True)
    if book_id is None:
        return go_back()
    if find_book(book_id) is None:
        print(f"\nError: Book ID {book_id} not found.")
        return False
    print("Leave a field blank to keep the current value.")
    new_title = input("New Title: ").strip()
    new_author = read_author("New Author: ", allow_blank=True)
    new_category = read_optional_subject()
    return print_result(edit_book(book_id, new_title, new_author, new_category))


def menu_remove_book():
    print(BACK_HINT)
    book_id = read_book_id("Enter Book ID to remove: ", allow_back=True)
    if book_id is None:
        return go_back()
    book = find_book(book_id)
    if book is None:
        print(f"\nError: Book ID {book_id} not found.")
        return False
    show_books([book], "BOOK TO REMOVE")
    if ask_yes_no("Remove this book? (y/n): "):
        return print_result(remove_book(book_id))
    print("\nRemoval cancelled.")
    return True


def menu_librarian_borrow_book():
    print(BACK_HINT)
    book_id = read_book_id("Enter Book ID to borrow: ", allow_back=True)
    if book_id is None:
        return go_back()
    student_id = read_student_id("Enter Student ID: ", allow_back=True)
    if student_id is None:
        return go_back()
    return print_result(borrow_book(book_id, student_id, date.today()))


def menu_librarian_return_book():
    print(BACK_HINT)
    book_id = read_book_id("Enter Book ID to return: ", allow_back=True)
    if book_id is None:
        return go_back()
    return print_result(return_book(book_id, date.today()))


# ---------- Student actions ----------
def menu_student_borrow_book(student_id):
    """Pick a subject, then pick one of the available books of that subject."""
    print("\nSelect a subject:")
    print_subject_list()
    print("[0] Back")
    choice = read_selection(f"Enter subject number (0-{len(SUBJECTS)}): ",
                            0, len(SUBJECTS))
    if choice == 0:
        return True
    subject = SUBJECTS[choice - 1]

    available = get_available_books_by_subject(subject)
    if not available:
        print(f"\nNo available books for {subject} right now.")
        return True

    print(f"\nAVAILABLE BOOKS - {subject.upper()}")
    for number, book in enumerate(available, start=1):
        print(f"[{number}] {book[B_TITLE]} by {book[B_AUTHOR]} (ID: {book[B_ID]})")
    print("[0] Back")
    pick = read_selection(f"Enter book number (0-{len(available)}): ",
                          0, len(available))
    if pick == 0:
        return True
    book = available[pick - 1]
    return print_result(borrow_book(book[B_ID], student_id, date.today()))


def menu_student_return_book(student_id):
    book_id = read_book_id("Enter Book ID to return: ")
    # a student may only return a book that they borrowed
    own_books = [t[T_BOOK] for t in get_student_loans(student_id)]
    if book_id not in own_books:
        print(f"\nError: You have not borrowed Book ID {book_id}.")
        return False
    return print_result(return_book(book_id, date.today()))


# ==========================================================
#  PART 5: REGISTRATION, LOGIN, AND DASHBOARDS
# ==========================================================
# ---------- Student registration (separate from login) ----------
def student_registration():
    print("\n--- STUDENT REGISTRATION ---")
    while True:
        student_id = read_student_id(f"Enter Student ID (e.g., {STUDENT_ID_EXAMPLE}): ")
        section = read_section(f"Enter Section (e.g., {SECTION_EXAMPLE}): ")
        success, message = register_student(student_id, section)
        print_result((success, message))
        if success:
            return
        if not ask_retry():
            return


# ---------- Student login (separate from registration) ----------
def student_login():
    """Returns the student ID if login works, or None if the user gives up."""
    print("\n--- STUDENT LOGIN ---")
    while True:
        student_id = read_student_id("Student ID: ")
        section = read_section("Section: ")
        if login_student(student_id, section):
            print(f"\n[SUCCESS] Welcome, {student_id}!")
            return student_id
        print("\nError: Student ID and Section do not match any registered student.")
        if not ask_retry():
            return None


# ---------- Librarian login (completely separate) ----------
def librarian_login():
    """Returns True if login works, or False if the user gives up or goes back."""
    print("\n--- LIBRARIAN LOGIN ---")
    print(BACK_HINT)
    while True:
        username = read_text("Username: ", allow_back=True)
        if username is None:
            go_back()
            return False
        password = read_text("Password: ", allow_back=True)
        if password is None:
            go_back()
            return False
        if login_librarian(username, password):
            print(f"\n[SUCCESS] Welcome, {username}!")
            return True
        print("\nError: Incorrect username or password. Please try again.")
        if not ask_retry():
            return False


# ---------- Student dashboard ----------
def print_student_menu():
    print("\n" + "=" * 34)
    print("      STUDENT DASHBOARD")
    print("=" * 34)
    print("[1] Search Book")
    print("[2] View All Books (Sorted)")
    print("[3] Borrow Book")
    print("[4] Return Book")
    print("[5] View My Borrowed Books")
    print("[6] Logout")
    print("=" * 34)


def student_dashboard(student_id):
    running = True
    while running:
        print_student_menu()
        choice = read_menu_choice(1, 6)

        if choice == 1:
            menu_search_book()
        elif choice == 2:
            menu_sort_books()
        elif choice == 3:
            repeat_until_done(lambda: menu_student_borrow_book(student_id))
        elif choice == 4:
            repeat_until_done(lambda: menu_student_return_book(student_id))
        elif choice == 5:
            show_transactions(get_student_loans(student_id), "MY BORROWED BOOKS")
        else:
            print("\nLogged out.")
            running = False


# ---------- Librarian dashboard ----------
def print_librarian_menu():
    print("\n" + "=" * 34)
    print("      LIBRARIAN DASHBOARD")
    print("=" * 34)
    print("[1] Manage Book")
    print("[2] View Records")
    print("[3] Borrowing")
    print("[4] Log Out")
    print("=" * 34)


def print_manage_book_menu():
    print("\n" + "=" * 34)
    print("          MANAGE BOOK")
    print("=" * 34)
    print("[1] Add Book")
    print("[2] Edit Book")
    print("[3] Remove Book")
    print("[4] Back")
    print("=" * 34)


def manage_book_menu():
    running = True
    while running:
        print_manage_book_menu()
        choice = read_menu_choice(1, 4)

        if choice == 1:
            repeat_until_done(menu_add_book)
        elif choice == 2:
            repeat_until_done(menu_edit_book)
        elif choice == 3:
            repeat_until_done(menu_remove_book)
        else:
            running = False


def print_view_records_menu():
    print("\n" + "=" * 34)
    print("          VIEW RECORDS")
    print("=" * 34)
    print("[1] Search Book")
    print("[2] View All Books (Sorted)")
    print("[3] View Available Books")
    print("[4] View Borrowed Books")
    print("[5] View Returned Books")
    print("[6] View Overdue Books")
    print("[7] View Transaction History")
    print("[8] View Students")
    print("[9] Back")
    print("=" * 34)


def view_records_menu():
    running = True
    while running:
        print_view_records_menu()
        choice = read_menu_choice(1, 9)

        if choice == 1:
            menu_search_book()
        elif choice == 2:
            menu_sort_books()
        elif choice == 3:
            show_books(get_available_books(), "AVAILABLE BOOKS")
        elif choice == 4:
            show_transactions(get_active_loans(), "CURRENTLY BORROWED BOOKS")
        elif choice == 5:
            show_transactions(get_returned_loans(), "RETURNED BOOKS")
        elif choice == 6:
            today = date.today()
            show_overdue_notices(get_overdue_loans(today), today)
        elif choice == 7:
            show_transactions(transactions, "TRANSACTION HISTORY")
        elif choice == 8:
            show_borrowers()
        else:
            running = False


def print_borrowing_menu():
    print("\n" + "=" * 34)
    print("            BORROWING")
    print("=" * 34)
    print("[1] Borrow Book")
    print("[2] Return Book")
    print("[3] Back")
    print("=" * 34)


def borrowing_menu():
    running = True
    while running:
        print_borrowing_menu()
        choice = read_menu_choice(1, 3)

        if choice == 1:
            repeat_until_done(menu_librarian_borrow_book)
        elif choice == 2:
            repeat_until_done(menu_librarian_return_book)
        else:
            running = False


def librarian_dashboard():
    running = True
    while running:
        print_librarian_menu()
        choice = read_menu_choice(1, 4)

        if choice == 1:
            manage_book_menu()
        elif choice == 2:
            view_records_menu()
        elif choice == 3:
            borrowing_menu()
        else:
            print("\nLogged out.")
            running = False


# ==========================================================
#  PART 6: MAIN SCREENS
# ==========================================================
def student_side():
    """Student screen: register or login (kept as two separate options)."""
    running = True
    while running:
        print("\n" + "=" * 34)
        print("          STUDENT")
        print("=" * 34)
        print("[1] Register")
        print("[2] Login")
        print("[3] Back")
        print("=" * 34)
        choice = read_menu_choice(1, 3)

        if choice == 1:
            student_registration()
        elif choice == 2:
            student_id = student_login()
            if student_id is not None:
                student_dashboard(student_id)
        else:
            running = False


def librarian_side():
    """Librarian screen: login, then the librarian dashboard."""
    if librarian_login():
        librarian_dashboard()


def main():
    print("=" * 50)
    print("   LIBRASENTINEL: LIBRARY MANAGEMENT SYSTEM")
    print("     PHINMA - Cagayan de Oro College")
    print("=" * 50)

    running = True
    while running:
        print("\n" + "=" * 34)
        print("       WELCOME - SELECT USER")
        print("=" * 34)
        print("[1] Student")
        print("[2] Librarian")
        print("[3] Exit")
        print("=" * 34)
        choice = read_menu_choice(1, 3)

        if choice == 1:
            student_side()
        elif choice == 2:
            librarian_side()
        else:
            print("\nExiting system. Thank you!")
            running = False


# ---------------------- RUN PROGRAM -----------------------
if __name__ == "__main__":
    main()
