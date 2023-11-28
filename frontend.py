from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

popup_response = False 

def show_popup(domain_name):
    global popup_response
    app = QApplication([])
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Website Productivity")
    msg_box.setText(f"Is the website {domain_name} productive?")
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    result = msg_box.exec_()
    print("RESULT : ", result)

    if result == QMessageBox.Yes:
        popup_response = True
    else:
        popup_response = False

    app.quit()

    return popup_response
    