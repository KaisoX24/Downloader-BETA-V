from tkinter import messagebox

def show_rate_limit_error():
    messagebox.showerror(
        "YouTube Rate Limit",
        "YouTube is temporarily blocking requests from your network.\n\n"
        "Possible solutions:\n"
        "• Wait 10-30 minutes\n"
        "• Change network / use VPN\n"
        "• Try again later\n\n"
        "This is not an app error."
    )

def show_cookie_error():
    messagebox.showerror(
        "Sign-in Required",
        "YouTube requires sign-in verification.\n\n"
        "Solutions:\n"
        "• Export cookies from your browser\n"
        "• Use a different network\n"
        "• Wait and try later\n\n"
        "This is a YouTube restriction."
    )

if __name__=='__main__':
    show_cookie_error()
    show_rate_limit_error()