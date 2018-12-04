# Another codesign tool for developer

This is a tool to sign enterprise ipa/app file using a (free) developer account, so you can debug app using XCode and webview using Safari.


## Usage

- Copy target ipa/app file under "Put_iPA_Here" folder
- Open "SignWithDeveloper" project
	- rename target "ModifyToYourTarget" to the name of your target app.
	- under "General/Signing" select a developer account. If generate certificate failed, choose a different bundle id.
	- Connect iOS device and make sure running target is your device.
	- Run Project, and wait for fail or a blank launch. Trust your developer certificate in iphone's "Setting/General"
	- Run Project Again, app will be installed into your device.(If App icon is not right,run again)