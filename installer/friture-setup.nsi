; NSIS Installer/Uninstaller script

!define PROJECT_PATH ".."

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "Friture"
!define /date PRODUCT_VERSION "%Y/%m/%d"
!define PRODUCT_PUBLISHER "Timothée Lecomte"
!define PRODUCT_DESCRIPTION "Real-time audio visualizations"
!define PRODUCT_WEB_SITE "http://tlecomte.github.com/friture/"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\friture.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

!define /date TIMESTAMP "%Y%m%d"

SetCompressor lzma

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Language Selection Dialog Settings
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "${PROJECT_PATH}\COPYING.txt"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\friture.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "friture-setup-${TIMESTAMP}.exe"
InstallDir "$PROGRAMFILES\Friture"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; Adds info to installer
VIProductVersion "0.0.0.0"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "Comments" "${PRODUCT_DESCRIPTION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "© ${PRODUCT_PUBLISHER} under the GNU GPLv3."
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "Installation for ${PRODUCT_NAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${PRODUCT_VERSION}"

Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Section "SectionPrincipale" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite try
  CreateDirectory "$SMPROGRAMS\Friture"
  CreateShortCut "$SMPROGRAMS\Friture\Friture.lnk" "$INSTDIR\friture.exe"
  CreateShortCut "$DESKTOP\Friture.lnk" "$INSTDIR\friture.exe"
  SetOutPath "$INSTDIR\imageformats"
  File "${PROJECT_PATH}\dist\imageformats\qsvg4.dll"
  SetOutPath "$INSTDIR"
  File "${PROJECT_PATH}\dist\library.zip"
  File "${PROJECT_PATH}\dist\*.pyd"
  File "${PROJECT_PATH}\dist\*.dll"
  File "${PROJECT_PATH}\dist\friture.exe"
  File "${PROJECT_PATH}\dist\w9xpopen.exe"
  File "${PROJECT_PATH}\COPYING.txt"
  File "${PROJECT_PATH}\README.md"
  File "${PROJECT_PATH}\TODO.txt"
SectionEnd

Section MSVC
  InitPluginsDir
  SetOutPath $PLUGINSDIR
  File "${PROJECT_PATH}\installer\vcredist_x86.exe"
  DetailPrint "Installing Visual C++ 2008 Libraries"
  ExecWait '"$PLUGINSDIR\vcredist_x86.exe" /qb!"'
SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\Friture\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\friture.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\friture.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) a été désinstallé avec succès de votre ordinateur."
FunctionEnd

Function un.onInit
!insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Êtes-vous certains de vouloir désinstaller totalement $(^Name) et tous ses composants ?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  RMDir /r "$INSTDIR"

  Delete "$SMPROGRAMS\Friture\Uninstall.lnk"
  Delete "$DESKTOP\Friture.lnk"
  Delete "$SMPROGRAMS\Friture\Friture.lnk"

  RMDir "$SMPROGRAMS\Friture"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Voulez-vous supprimer les réglages de Friture précédemment sauvegardés ?" IDNO +2
  DeleteRegKey HKCU "Software\Friture"
  
  SetAutoClose true
SectionEnd