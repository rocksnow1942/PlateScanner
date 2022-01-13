from ScannerApp import ScannerApp



# run app with -dev to avoid authentication page to scan user badge.
# in the config.ini, set appMode to dev or prod to switch between devMode and prodMode
app = ScannerApp()
app.protocol('WM_DELETE_WINDOW',app.on_closing)
app.mainloop()
