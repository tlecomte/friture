; NSIS Installer/Uninstaller script

!define PROJECT_PATH ".."

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "Friture"
!define PRODUCT_PUBLISHER "Timothée Lecomte"
!define PRODUCT_DESCRIPTION "Real-time audio visualizations"
!define PRODUCT_WEB_SITE "http://www.friture.org"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\friture.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_LICENSE "GNU GPL v3"

!define /date TIMESTAMP "%Y%m%d"

; read version from Python source file
!searchparse /noerrors /file ${PROJECT_PATH}\friture\__init__.py '__version__ = "' VERSION_SHORT '"'
!searchparse /noerrors /file ${PROJECT_PATH}\friture\__init__.py '__versionXXXX__ = "' VERSION_XXXX '"'

SetCompressor lzma

!include "MUI2.nsh"

; MUI Settings

; show a message box with a warning when the user wants to close the installer
!define MUI_ABORTWARNING
; same for uninstaller
!define MUI_UNABORTWARNING

; Language Selection Dialog Settings
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

; Installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${PROJECT_PATH}\COPYING.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
; offer to run the program when exiting
!define MUI_FINISHPAGE_RUN "$INSTDIR\friture.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language files
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"

; Reserve files (won't be compressed with the rest, to start faster)
!insertmacro MUI_RESERVEFILE_LANGDLL ;Language selection dialog

; MUI end ------

Name "${PRODUCT_NAME} ${VERSION_SHORT}"
OutFile "friture-${VERSION_SHORT}-${TIMESTAMP}.exe"
InstallDir "$PROGRAMFILES\Friture"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; Adds info to installer
VIProductVersion "${VERSION_XXXX}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "Comments" "${PRODUCT_DESCRIPTION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "© ${PRODUCT_PUBLISHER} under the ${PRODUCT_LICENSE}."
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "${PRODUCT_NAME} installer"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${VERSION_XXXX}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductVersion" "${VERSION_XXXX}"

Function .onInit
  ; display a language selection dialog
  !insertmacro MUI_LANGDLL_DISPLAY

  ; detect if a previous version was installed
  ReadRegStr $R0 ${PRODUCT_UNINST_ROOT_KEY} ${PRODUCT_UNINST_KEY} "UninstallString"
  StrCmp $R0 "" done

  ; ask the user to uninstall the previous version
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
  "${PRODUCT_NAME} is already installed. $\n$\nClick `OK` to remove the \
  previous version or `Cancel` to cancel this upgrade." \
  IDOK uninst
  Abort

  ;Run the uninstaller
  uninst:
    ClearErrors
    Exec $INSTDIR\uninst.exe

  done:
FunctionEnd

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite try
  CreateDirectory "$SMPROGRAMS\Friture"
  CreateShortCut "$SMPROGRAMS\Friture\Friture.lnk" "$INSTDIR\friture.exe"
  CreateShortCut "$DESKTOP\Friture.lnk" "$INSTDIR\friture.exe"

  SetOutPath "$INSTDIR\_sounddevice_data"
  File "${PROJECT_PATH}\dist\friture\_sounddevice_data\*"

  SetOutPath "$INSTDIR\qt5_plugins"
  File /r "${PROJECT_PATH}\dist\friture\qt5_plugins\*"

  SetOutPath "$INSTDIR"
  File "${PROJECT_PATH}\dist\friture\base_library.zip"
  File "${PROJECT_PATH}\dist\friture\*.pyd"
  ; take all dlls except icudt*.dll which will be taken from the installer folder, where a stripped down version is stored
  File /x icudt*.dll "${PROJECT_PATH}\dist\friture\*.dll"
  File "${PROJECT_PATH}\installer\icudt*.dll"
  File "${PROJECT_PATH}\dist\friture\friture.exe"
  File "${PROJECT_PATH}\COPYING.txt"
  File "${PROJECT_PATH}\README.rst"
  File "${PROJECT_PATH}\TODO.txt"
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
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${VERSION_SHORT}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

Function un.onInit
  ; use the language of the installer
  !insertmacro MUI_UNGETLANGUAGE
FunctionEnd

LangString STR_remove_settings ${LANG_ENGLISH} "Do you want to remove Friture saved settings ?"
; Warning: the following line should be encoded in CP1252
LangString STR_remove_settings ${LANG_FRENCH} "Voulez-vous supprimer les réglages de Friture précédemment sauvegardés ?"

Section Uninstall
  RMDir /r "$INSTDIR"

  Delete "$SMPROGRAMS\Friture\Uninstall.lnk"
  Delete "$DESKTOP\Friture.lnk"
  Delete "$SMPROGRAMS\Friture\Friture.lnk"

  RMDir "$SMPROGRAMS\Friture"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 $(STR_remove_settings) IDNO +2
  DeleteRegKey HKCU "Software\Friture"

  SetAutoClose true
SectionEnd