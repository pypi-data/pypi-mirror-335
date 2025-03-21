"""Functions creating objects for survey structure classes"""

from json import dumps, loads
from .models import *
from .helperModels import ValidatorModel
from .utils import flatten
from .validators import expressionValidator


def survey(
    *pages: PageModel | list[PageModel],
    addCode: dict | None = None,
    addScoreToResults: bool = True,
    allowResizeComment: bool = True,
    autoAdvanceAllowComplete: bool = True,
    autoAdvanceEnabled: bool = False,
    autoFocusFirstError: bool = True,
    autoFocusFirstQuestion: bool = False,
    autoGrowComment: bool = False,
    backgroundImage: str | None = None,
    backgroundOpacity: int = 1,
    build: bool = True,
    calculatedValues: list[dict] | None = None,
    checkErrorsMode: str = "onNextPage",
    commentAreaRows: int = 2,
    completeText: str | None = None,
    completedBeforeHtml: str | None = None,
    completedHtml: str | None = None,
    completedHtmlOnCondition: list[dict] | None = None,
    cookieName: str | None = None,
    editText: str | None = None,
    firstPageIsStartPage: bool | None = None,
    folderName: str = "survey",
    locale: str = "en",
    logo: str | None = None,
    logoFit: str = "contain",
    logoHeight: str = "40px",
    logoPosition: str = "left",
    logoWidth: str = "auto",
    matrixDragHandleArea: str = "entireItem",
    maxCommentLength: int = 0,
    maxTextLength: int = 0,
    mode: str = "edit",
    navigateToUrl: str | None = None,
    navigateToUrlOnCondition: list[dict] | None = None,
    numberOfGroups: int = 1,
    pageNextText: str | None = None,
    pagePrevText: str | None = None,
    path: str | Path = os.getcwd(),
    previewText: str | None = None,
    progressBarInheritWidthFrom: str = "container",
    progressBarShowPageNumbers: bool = False,
    progressBarShowPageTitles: bool = False,
    progressBarType: str = "pages",
    questionDescriptionLocation: str = "underTitle",
    questionErrorLocation: str = "top",
    questionOrder: str = "initial",
    questionStartIndex: int | str | None = None,
    questionTitleLocation: str = "top",
    questionTitlePattern: str = "numTitleRequire",
    questionsOnPageMode: str = "standard",
    requiredMark: str = "*",
    scoresSuffix: str = "_score",
    showCompletePage: bool = True,
    showNavigationButtons: str = "bottom",
    showPageNumbers: bool | None = None,
    showPageTitles: bool = True,
    showPrevButton: bool = True,
    showPreviewBeforeComplete: str = "noPreview",
    showProgressBar: str = "off",
    showQuestionNumbers: bool | str = False,
    showTOC: bool = False,
    showTimer: bool = False,
    showTimerOnlyWhenLimit: bool = False,
    showTitle: bool = True,
    startSurveyText: str | None = None,
    storeOthersAsComment: bool = True,
    textUpdateMode: str = "onBlur",
    themeFile: Path | str | None = None,
    timeLimit: int | None = None,
    timeLimitPerPage: int | None = None,
    timerInfoMode: str = "combined",
    timerLocation: str = "top",
    title: str | None = None,
    tocLocation: str = "left",
    triggers: list[dict] | None = None,
    urlParameters: str | list[str] | None = None,
    validateVisitedEmptyFields: bool = False,
    validationEnabled: bool = True,
    width: str | None = None,
    widthMode: str = "auto",
    **kwargs,
) -> SurveyModel:
    """Create a survey object

    Args:
        pages (list[PageModel]): The pages of the survey.
        build (bool): Whether to build the survey. Default is True.
        addCode (dict | None): Additional code for the survey. Usually not necessary.
        addScoreToResults (bool): Whether to add the scores of the questions with `correctAnswer` to the results data. See `scoresSuffix`.
        allowResizeComment (bool): Whether to allow resizing the long questions input area. Default is True. Can be overridden for individual questions.
        autoAdvanceAllowComplete (bool): Whether the survey should complete automatically after all questions on the last page had been answered. Works only if `autoAdvanceEnabled=True`. Default is True.
        autoAdvanceEnabled (bool): Whether to go to the next page automatically after all questions had been answered. Default is False.
        autoFocusFirstError (bool): Whether to focus on the first error if it was raised. Default is True.
        autoFocusFirstQuestion (bool): Whether to focus the first question automatically. Default is False.
        autoGrowComment (bool): Whether to automatically grow the long questions input area. Default is False. Can be overridden for individual questions.
        backgroundImage (str | None): URL or base64 of the background image.
        backgroundOpacity (int): The opacity of the background image. 0 is transparent, 1 is opaque.
        calculatedValues (list[dict] | None): The calculated values for the survey. List of dictionaries with keys `name`, `expression` and optionally `includeIntoResult` (bool) to save the value in the db.
        checkErrorsMode (str): The mode of checking errors. Can be 'onNextPage', 'onValueChanged', 'onComplete'.
        commentAreaRows (int): The number of rows for the comment area of the questions with `showCommentArea` or `showOtherItem` set to True. Default is 2. Can be overridden for individual questions.
        completeText (str | None): Text for the 'Complete' button.
        completedBeforeHtml (str | None): HTML content to show if the survey had been completed before. Use with `cookieName`.
        completedHtml (str | None): HTML content to show after the survey is completed.
        completedHtmlOnCondition (list[dict] | None): HTML content to show after the survey is completed if the condition is met. List of dictionaries with keys `expression` and `html` keys.
        cookieName (str | None): The name of the cookie to store the information about the survey having been completed. See `completedBeforeHtml`.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        editText (str | None): Text for the 'Edit' button if `showPreviewBeforeComplete=True`.
        firstPageIsStartPage (bool | None): Whether the first page is a start page. Default is False.
        locale (str): The locale of the survey. Default is 'en'.
        logo (str | None): URL or base64 of the logo image.
        logoFit (str): The `object-fit` CSS property logo image. Can be 'contain', 'cover', 'fill', 'none'.
        logoHeight (str): The height of the logo image in CSS units. Default is '40px'.
        logoPosition (str): The position of the logo image. Can be 'left', 'right', 'none'.
        logoWidth (str): The width of the logo image in CSS units. Default is 'auto'.
        matrixDragHandleArea (str): The part of an item with which the users can drag and drop in dynamic matrix questions. Can be 'entireItem' (default), 'icon' (drag icon only).
        maxCommentLength (int): The maximum length of the comment area in the questions with `showOtherItem` or `showCommentArea` set to True. Default is 0 (no limit).
        maxTextLength (int): The maximum length of the text in the textual questions. Default is 0 (no limit).
        mode (str): The mode of the survey. Can be 'edit' (can be filled), 'display' (read-only).
        navigateToUrl (str | None): URL to navigate to after the survey is completed.
        navigateToUrlOnCondition (list[dict] | None): URL to navigate to after the survey is completed if the condition is met. List of dictionaries with keys `expression` and `url` keys.
        pageNextText (str | None): Text for the 'Next' button.
        pagePrevText (str | None): Text for the 'Previous' button.
        previewText (str | None): Text for the 'Preview' button if `showPreviewBeforeComplete=True`.
        progressBarInheritWidthFrom (str): The element from which the progress bar should inherit the width. Can be 'container', 'survey'.
        progressBarShowPageNumbers (bool): Whether to show the page numbers on the progress bar. Only if `progressBarType="pages"`. Default is False. See `showProgressBar`.
        progressBarShowPageTitles (bool): Whether to show the page titles on the progress bar. Only if `progressBarType="pages"`. Default is False. See `showProgressBar`.
        progressBarType (str): The type of the progress bar. Can be 'pages' (default), 'questions', 'requiredQuestions', 'correctQuestions'.
        questionDescriptionLocation (str): The location of the description for the questions. Can be 'underTitle' (default), 'underInput'. Can be overridden for individual questions.
        questionErrorLocation (str): The location of the error text for the questions. Can be 'top' (default), 'bottom'. Can be overridden for individual questions.
        questionOrder (str): The order of the questions. Can be 'initial' (default), 'random'. Can be overridden for individual pages.
        questionStartIndex (int | str | None): The number or letter with which the questions numbering should start.
        questionTitleLocation (str): The location of the title for the questions. Can be 'top' (default), 'bottom', 'left'. Can be overridden for individual questions or pages.
        questionTitlePattern (str): The pattern of the question title. See <https://surveyjs.io/form-library/documentation/design-survey/configure-question-titles#title-pattern>.
        questionsOnPageMode (str): The mode of the questions on the page. Can be 'standard' (default; use structure in JSON), 'singlePage' (combine all questions into a single page), 'questionPerPage' (move all questions to separate pages).
        requiredMark (str): The text denoting the required questions. Default is '*'.
        scoresSuffix (str): The suffix of the score column if `addScoreToResults=True`. Default is '_score'.
        showCompletePage (bool): Whether to show the completed page. Default is True.
        showNavigationButtons (str): The location of the navigation buttons. Can be 'bottom' (default), 'top', 'both', 'none'.
        showPageNumbers (bool | None): Whether to show the page numbers in the pages' titles.
        showPageTitles (bool): Whether to show the page titles. Default is True.
        showPrevButton (bool): Whether to show the 'Previous' button. Default is True.
        showPreviewBeforeComplete (str): Whether to preview all answers before completion. Can be 'noPreview' (default), 'showAllQuestions', 'showAnsweredQuestions'.
        showProgressBar (str): Whether to show the progress bar. Can be 'off' (default), 'aboveHeader', 'belowHeader', 'bottom', 'topBottom', 'auto'.
        showQuestionNumbers (bool | str): Whether to show the question numbers. Default is False. Can be True, 'on', False, 'off', 'onpage' (number each page anew).
        showTOC (bool): Whether to show the table of contents. Default is False. See `tocLocation`.
        showTimer (bool): Whether to show the timer. Default is False. If the timer is shown, it automatically starts measuring time. See `timerInfoMode`, `timerLocation`, `timeLimit`, and `timeLimitPerPage`.
        showTimerOnlyWhenLimit (bool): Whether the timer should be shown only when there is a time limit on a page and disappear when the time is not limited (`True`) or be visible on all pages (`False`, default).
        showTitle (bool): Whether to show the survey title. Default is True.
        startSurveyText (str | None): Text for the 'Start' button if `firstPageIsStartPage=True`.
        storeOthersAsComment (bool): Whether to store the 'Other' answers in a separate column (True; see `commentSuffix`) or in the question column (False). Default is True.
        textUpdateMode (str): The mode of updating the text. Can be 'onBlur' (default; update after the field had been unclicked), 'onTyping' (update every key press). Can be overridden for individual questions.
        themeFile (Path | str | None): The path to the theme file. If None, default is used. Use the [theme builder](https://surveyjs.io/create-free-survey) to create a theme file.
        timeLimit (int | None): Maximum time in seconds to finish the survey. Default is None (no limit). You probably want to set `showTimerOnlyWhenLimit` to False when using this option.
        timeLimitPerPage (int | None): Maximum time in seconds to finish the page. 0 means no limit. You probably want to set `showTimerOnlyWhenLimit` to False when using this option.
        timerInfoMode (str): What times to show on the timer panel. Can be 'all' (default), 'page', 'survey'. See `showTimer`.
        timerLocation (str): Where to show the timer if `showTimer` is True. Can be 'top` (default) or 'bottom'.
        title (str | None): The title of the survey.
        tocLocation (str): The location of the table of contents. Can be 'left' (default), 'right'. See `showTOC`.
        triggers (str | None): Triggers for the survey. Usually not necessary. See <https://surveyjs.io/form-library/documentation/design-survey/conditional-logic#conditional-survey-logic-triggers>.
        urlParameters (list[str] | None): The URL parameters to be expected and saved. Default is None.
        validateVisitedEmptyFields (bool): Whether to validate empty fields that had been clicked, and unclicked empty. Default is False.
        validationEnabled (bool): Whether to validate the values of the questions. Default is True.
        width (str | None): Width of the survey in CSS units. Default is None (inherit from the container).
        widthMode (str): The mode of the width. Can be 'auto' (default; the width is set by the content), 'static', 'responsive'.

    """
    if not isinstance(urlParameters, list):
        urlParameters = [urlParameters] if urlParameters else None
    args = {
        "addScoreToResults": addScoreToResults,
        "autoAdvanceAllowComplete": autoAdvanceAllowComplete,
        "allowResizeComment": allowResizeComment,
        "autoGrowComment": autoGrowComment,
        "backgroundImage": backgroundImage,
        "backgroundOpacity": backgroundOpacity,
        "calculatedValues": calculatedValues,
        "checkErrorsMode": checkErrorsMode,
        "commentAreaRows": commentAreaRows,
        "completedBeforeHtml": completedBeforeHtml,
        "completedHtml": completedHtml,
        "completedHtmlOnCondition": completedHtmlOnCondition,
        "completeText": completeText,
        "cookieName": cookieName,
        "editText": editText,
        "firstPageIsStartPage": firstPageIsStartPage,
        "autoFocusFirstQuestion": autoFocusFirstQuestion,
        "autoFocusFirstError": autoFocusFirstError,
        "autoAdvanceEnabled": autoAdvanceEnabled,
        "locale": locale,
        "logo": logo,
        "logoFit": logoFit,
        "logoHeight": logoHeight,
        "logoPosition": logoPosition,
        "logoWidth": logoWidth,
        "matrixDragHandleArea": matrixDragHandleArea,
        "maxCommentLength": maxCommentLength,
        "maxTextLength": maxTextLength,
        "timeLimit": timeLimit,
        "timeLimitPerPage": timeLimitPerPage,
        "mode": mode,
        "navigateToUrl": navigateToUrl,
        "navigateToUrlOnCondition": navigateToUrlOnCondition,
        "numberOfGroups": numberOfGroups,
        "pageNextText": pageNextText,
        "pagePrevText": pagePrevText,
        "previewText": previewText,
        "progressBarInheritWidthFrom": progressBarInheritWidthFrom,
        "progressBarShowPageNumbers": progressBarShowPageNumbers,
        "progressBarShowPageTitles": progressBarShowPageTitles,
        "progressBarType": progressBarType,
        "questionDescriptionLocation": questionDescriptionLocation,
        "questionErrorLocation": questionErrorLocation,
        "questionsOnPageMode": questionsOnPageMode,
        "questionOrder": questionOrder,
        "questionStartIndex": questionStartIndex,
        "questionTitleLocation": questionTitleLocation,
        "questionTitlePattern": questionTitlePattern,
        "requiredMark": requiredMark,
        "scoresSuffix": scoresSuffix,
        "showCompletePage": showCompletePage,
        "showNavigationButtons": showNavigationButtons,
        "showPageNumbers": showPageNumbers,
        "showPageTitles": showPageTitles,
        "showPrevButton": showPrevButton,
        "showPreviewBeforeComplete": showPreviewBeforeComplete,
        "showProgressBar": showProgressBar,
        "showQuestionNumbers": showQuestionNumbers,
        "showTimer": showTimer,
        "showTimerOnlyWhenLimit": showTimerOnlyWhenLimit,
        "timerInfoMode": timerInfoMode,
        "timerLocation": timerLocation,
        "showTitle": showTitle,
        "showTOC": showTOC,
        "startSurveyText": startSurveyText,
        "storeOthersAsComment": storeOthersAsComment,
        "textUpdateMode": textUpdateMode,
        "title": title,
        "themeFile": themeFile,
        "tocLocation": tocLocation,
        "triggers": triggers,
        "urlParameters": urlParameters,
        "validateVisitedEmptyFields": validateVisitedEmptyFields,
        "validationEnabled": validationEnabled,
        "width": width,
        "widthMode": widthMode,
        "addCode": addCode,
    }
    pages = flatten(pages)
    surveyObject = SurveyModel(pages=pages, **args, **kwargs)
    if build:
        surveyObject.build(path=path, folderName=folderName)
    return surveyObject


def page(
    name: str,
    *questions: QuestionModel | list[QuestionModel],
    addCode: dict | None = None,
    description: str | None = None,
    enableIf: str | None = None,
    id: str | None = None,
    isRequired: bool = False,
    maxWidth: str = "100%",
    minWidth: str = "300px",
    navigationButtonsVisibility: str = "inherit",
    navigationDescription: str | None = None,
    navigationTitle: str | None = None,
    questionErrorLocation: str = "default",
    questionOrder: str = "default",
    questionTitleLocation: str = "default",
    readOnly: bool = False,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    state: str = "default",
    timeLimit: int | None = None,
    timeMinimum: int | None = None,
    title: str | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    visibleIndex: int | None = None,
    **kwargs,
) -> PageModel:
    """Create a page object

    Args:
        name (str): The label of the page.
        questions (QuestionModel | list[QuestionModel]): The questions on the page.
        addCode (dict | None): Additional code for the survey. Usually not necessary.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        description (str | None): Optional subtitle or description of the page.
        enableIf (str | None): Expression to enable the page.
        id (str | None): HTML id attribute for the page. Usually not necessary.
        isRequired (bool): Whether the page is required (at least one question must be answered).
        maxWidth (str): Maximum width of the page in CSS units.
        minWidth (str): Minimum width of the page in CSS units.
        navigationButtonsVisibility (str): The visibility of the navigation buttons. Can be 'inherit', 'show', 'hide'.
        navigationDescription (str | None): Description for the page navigation.
        navigationTitle (str | None): Title for the page navigation.
        questionErrorLocation (str): The location of the error text for the questions. Can be 'default', 'top', 'bottom'.
        questionOrder (str): The order of the questions. Can be 'default', 'random'.
        questionTitleLocation (str): The location of the title for the questions. Can be 'default', 'top', 'bottom'.
        readOnly (bool): Whether the page is read-only.
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the page required (at least one question must be answered).
        state (str): If the page should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        timeLimit (int | None): Maximum time in seconds to finish the page.
        timeMinimum (int | None): Minimum time in seconds the user has to spend on the page. All navigation buttons are hidden during this period.
        title (str): The visible title of the page.
        visible (bool): Whether the page is visible.
        visibleIf (str | None): Expression to make the page visible.
        visibleIndex (int | None): The index at which the page should be visible.
        width (str): Width of the page
    """
    args = {
        "description": description,
        "enableIf": enableIf,
        "id": id,
        "isRequired": isRequired,
        "timeLimit": timeLimit,
        "timeMinimum": timeMinimum,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "navigationButtonsVisibility": navigationButtonsVisibility,
        "navigationDescription": navigationDescription,
        "navigationTitle": navigationTitle,
        "questionErrorLocation": questionErrorLocation,
        "questionTitleLocation": questionTitleLocation,
        "questionOrder": questionOrder,
        "readOnly": readOnly,
        "requiredErrorText": requiredErrorText,
        "requiredIf": requiredIf,
        "state": state,
        "title": title,
        "visible": visible,
        "visibleIf": visibleIf,
        "visibleIndex": visibleIndex,
        "addCode": addCode,
    }
    questions = flatten(questions)
    return PageModel(
        name=name,
        questions=questions,
        **args,
        **kwargs,
    )


def panel(
    name: str,
    *questions: QuestionModel | list[QuestionModel],
    description: str | None = None,
    enableIf: str | None = None,
    id: str | None = None,
    innerIndent: int | None = None,
    isRequired: bool = False,
    maxWidth: str = "100%",
    minWidth: str = "300px",
    questionErrorLocation: str = "default",
    questionOrder: str = "default",
    questionStartIndex: str | None = None,
    questionTitleLocation: str = "default",
    questionTitleWidth: str | None = None,
    readOnly: bool = False,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    rightIndent: int | None = None,
    showNumber: bool = False,
    showQuestionNumbers: str = "default",
    startWithNewLine: bool = True,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> PanelModel:
    """
    Create a panel.

    Args:
        name (str): The label of the page.
        questions (QuestionModel | list[QuestionModel]): The questions on the panel.
        description (str | None): Optional subtitle or description of the panel.
        enableIf (str | None): Expression to enable the panel.
        id (str | None): HTML id attribute for the panel. Usually not necessary.
        innerIndent (int | None): The inner indent of the panel.
        isRequired (bool): Whether the panel is required (at least one question must be answered).
        maxWidth (str): Maximum width of the panel in CSS units.
        minWidth (str): Minimum width of the panel in CSS units.
        questionErrorLocation (str): The location of the error text for the questions. Can be 'default', 'top', 'bottom'.
        questionOrder (str): The order of the questions. Can be 'default', 'random'.
        questionStartIndex (str | None): The number or letter with which the questions numbering should start.
        questionTitleLocation (str): The location of the title for the questions. Can be 'default', 'top', 'bottom'.
        questionTitleWidth (str | None): The width of the question title.
        readOnly (bool): Whether the panel is read-only.
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the panel required (at least one question must be answered).
        rightIndent (int | None): The right indent of the panel.
        showNumber (bool): Whether to show the panel number.
        showQuestionNumbers (str): Whether to show the question numbers. Can be 'default', 'on', 'off', 'onpage' (number each page anew).
        startWithNewLine (bool): Whether to start the panel on a new line.
        visible (bool): Whether the panel is visible.
        visibleIf (str | None): Expression to make the panel visible.
        width (str): Width of the panel.
    """
    args = {
        "description": description,
        "enableIf": enableIf,
        "id": id,
        "innerIndent": innerIndent,
        "isRequired": isRequired,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "questionErrorLocation": questionErrorLocation,
        "questionOrder": questionOrder,
        "questionStartIndex": questionStartIndex,
        "questionTitleLocation": questionTitleLocation,
        "questionTitleWidth": questionTitleWidth,
        "readOnly": readOnly,
        "requiredErrorText": requiredErrorText,
        "requiredIf": requiredIf,
        "rightIndent": rightIndent,
        "showNumber": showNumber,
        "showQuestionNumbers": showQuestionNumbers,
        "startWithNewLine": startWithNewLine,
        "visible": visible,
        "visibleIf": visibleIf,
        "width": width,
    }
    questions = flatten(questions)
    return PanelModel(
        name=name,
        questions=questions,
        **args,
        **kwargs,
    )


def dropdown(
    name: str,
    title: str | list[str] | None,
    *choices: str | dict | list,
    addCode: dict | None = None,
    choicesFromQuestion: str | None = None,
    choicesFromQuestionMode: str = "all",
    choicesMax: int | None = None,
    choicesMin: int | None = None,
    choicesOrder: str = "none",
    choicesStep: int | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    dontKnowText: str | None = None,
    enableIf: str | None = None,
    errorLocation: str = "default",
    hideIfChoicesEmpty: bool | None = None,
    id: str | None = None,
    isRequired: bool = False,
    maxWidth: str = "100%",
    minWidth: str = "300px",
    noneText: str | None = None,
    otherErrorText: str | None = None,
    otherText: str | None = None,
    placeholder: str | None = None,
    readOnly: bool = False,
    refuseText: str | None = None,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showDontKnowItem: bool = False,
    showNoneItem: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    showRefuseItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionDropdownModel | list[QuestionDropdownModel]:
    """Create a single-select dropdown question object

    Args:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        choices (str | dict | list): The choices for the question. Can be string(s) or dictionary(-ies) with structure `{"value": ..., "text": ...}`. You can also add `visibleIf`, `enableIf`, and `requiredIf` to the dictionary.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        choicesFromQuestion (str | None): The name of the question to get the choices from if the are to be copied. Use with `choicesFromQuestionMode`.
        choicesFromQuestionMode (str): The mode of copying choices. Can be 'all', 'selected', 'unselected'.
        choicesMax (int | None): Maximum for automatically generated choices. Use with `choicesMin` and `choicesStep`.
        choicesMin (int | None): Minimum for automatically generated choices. Use with `choicesMax` and `choicesStep`.
        choicesOrder (str): The order of the choices. Can be 'none', 'asc', 'desc', 'random'.
        choicesStep (int | None): Step for automatically generated choices. Use with `choicesMax` and `choicesMin`.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        dontKnowText: str | None = None
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        hideIfChoicesEmpty (bool | None): Whether to hide the question if there are no choices.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isRequired (bool): Whether the question is required.
        maxWidth (str): Maximum width of the question in CSS units.
        minWidth (str): Minimum width of the question in CSS units.
        noneText (str | None): Text for the 'None' choice.
        otherErrorText (str | None): Error text no text for the 'Other' choice.
        otherText (str | None): Text for the 'Other' choice.
        placeholder (str | None): Placeholder text.
        readOnly (bool): Whether the question is read-only.
        refuseText: str | None = None
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showDontKnowItem (bool): Show don't know option. Defaults to `False`.
        showNoneItem (bool): Show none option. Defaults to `False`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        showRefuseItem (bool): Show refuse option. Defaults to `False`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "choicesFromQuestion": choicesFromQuestion,
        "choicesFromQuestionMode": choicesFromQuestionMode,
        "choicesOrder": choicesOrder,
        "showDontKnowItem": showDontKnowItem,
        "dontKnowText": dontKnowText,
        "hideIfChoicesEmpty": hideIfChoicesEmpty,
        "showNoneItem": showNoneItem,
        "noneText": noneText,
        "otherText": otherText,
        "otherErrorText": otherErrorText,
        "showRefuseItem": showRefuseItem,
        "refuseText": refuseText,
        "choicesMax": choicesMax,
        "choicesMin": choicesMin,
        "choicesStep": choicesStep,
        "placeholder": placeholder,
    }
    choices = flatten(choices)
    if not isinstance(title, list):
        title = [title]
    if len(title) != 1:
        return [
            QuestionDropdownModel(
                name=f"{name}_{i+1}", title=t, choices=choices, **args, **kwargs
            )
            for i, t in enumerate(title)
        ]
    else:
        return QuestionDropdownModel(
            name=name, title=title[0], choices=choices, **args, **kwargs
        )


def text(
    name: str,
    *title: str | list[str] | None,
    addCode: dict | None = None,
    autocomplete: str | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    enableIf: str | None = None,
    errorLocation: str = "default",
    id: str | None = None,
    inputSize: int | None = None,
    inputType: str = "text",
    isRequired: bool = False,
    max: str | int | None = None,
    maxErrorText: str | None = None,
    maxLength: int | None = None,
    maxValueExpression: str | None = None,
    maxWidth: str = "100%",
    min: str | int | None = None,
    minErrorText: str | None = None,
    minValueExpression: str | None = None,
    minWidth: str = "300px",
    monitorInput: bool = False,
    placeholder: str | None = None,
    readOnly: bool = False,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    step: str | None = None,
    textUpdateMode: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionTextModel:
    """Create a text question object

    Args:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        autocomplete (str | None): A value of `autocomplete` attribute for `<input>`. See MDN for a list: <https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/autocomplete#token_list_tokens>.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        inputSize (int | None): The width of the input in characters. A value for `inputSize` attribute of `<input>`.
        inputType (str | None): The type of the input. Can be 'text', 'password', 'email', 'url', 'tel', 'number', 'date', 'datetime-local', 'time', 'month', 'week', 'color'.
        isRequired (bool): Whether the question is required.
        max (str): The `max` attribute of `<input>`. Syntax depends on the `inputType`. See MDN for details: <https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/max>.
        maxErrorText (str | None): Error text if the value exceeds `max`.
        maxLength (int | None): The maximum length of the input in characters. Use 0 for no limit. Use -1 for the default limit.
        maxValueExpression (str | None): Expression to decide the maximum value.
        maxWidth (str): Maximum width of the question in CSS units.
        min (str | None): The `min` attribute of `<input>`. Syntax depends on the `inputType`. See MDN for details: <https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/min>.
        minErrorText (str | None): Error text if the value is less than `min`.
        minValueExpression (str | None): Expression to decide the minimum value.
        minWidth (str): Minimum width of the question in CSS units.
        monitorInput (bool): Whether to count the time spent with the question focused and the number of key presses. Useful for bot detection.
        placeholder (str | None): Placeholder text for the input.
        readOnly (bool): Whether the question is read-only.
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        step (str | None): The `step` attribute of `<input>`. Syntax depends on the `inputType`. See MDN for details: <https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/step>.
        textUpdateMode (str): The mode of updating the text. Can be 'default', 'onBlur' (update after the field had been unclicked), 'onTyping' (update every key press).
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "autocomplete": autocomplete,
        "inputType": inputType,
        "max": max,
        "maxErrorText": maxErrorText,
        "maxLength": maxLength,
        "maxValueExpression": maxValueExpression,
        "min": min,
        "minErrorText": minErrorText,
        "minValueExpression": minValueExpression,
        "monitorInput": monitorInput,
        "placeholder": placeholder,
        "inputSize": inputSize,
        "step": step,
        "textUpdateMode": textUpdateMode,
    }
    title = flatten(title)
    if len(title) != 1:
        return [
            QuestionTextModel(name=f"{name}_{i+1}", title=t, **args, **kwargs)
            for i, t in enumerate(title)
        ]
    return QuestionTextModel(name=name, title=title[0], **args, **kwargs)


def checkbox(
    name: str,
    title: str | list[str] | None,
    *choices: str | dict | list,
    addCode: dict | None = None,
    choicesFromQuestion: str | None = None,
    choicesFromQuestionMode: str = "all",
    choicesOrder: str = "none",
    colCount: int | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    dontKnowText: str | None = None,
    enableIf: str | None = None,
    errorLocation: str = "default",
    hideIfChoicesEmpty: bool | None = None,
    id: str | None = None,
    isAllSelected: bool | None = None,
    isRequired: bool = False,
    maxSelectedChoices: int = 0,
    maxWidth: str = "100%",
    minSelectedChoices: int = 0,
    minWidth: str = "300px",
    noneText: str | None = None,
    otherErrorText: str | None = None,
    otherText: str | None = None,
    readOnly: bool = False,
    refuseText: str | None = None,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    selectAllText: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showDontKnowItem: bool = False,
    showNoneItem: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    showRefuseItem: bool = False,
    showSelectAllItem: bool | None = None,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionCheckboxModel | list[QuestionCheckboxModel]:
    """Create a checkbox question object

    Args:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        choices (str | dict | list): The choices for the question. Can be string(s) or dictionary(-ies) with structure `{"value": ..., "text": ...}`. You can also add `visibleIf`, `enableIf`, and `requiredIf` to the dictionary.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        choicesFromQuestion (str | None): The name of the question to get the choices from if the are to be copied. Use with `choicesFromQuestionMode`.
        choicesFromQuestionMode (str): The mode of copying choices. Can be 'all', 'selected', 'unselected'.
        choicesOrder (str): The order of the choices. Can be 'none', 'asc', 'desc', 'random'.
        colCount (int | None): The number of columns for the choices. 0 means a single line.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        dontKnowText: str | None = None
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        hideIfChoicesEmpty (bool | None): Whether to hide the question if there are no choices.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isAllSelected (bool | None): Start with all choices selected. Default is False.
        isRequired (bool): Whether the question is required.
        maxSelectedChoices (int): Maximum number of selected choices. 0 means no limit.
        maxWidth (str): Maximum width of the question in CSS units.
        minSelectedChoices (int): Minimum number of selected choices. 0 means no limit.
        minWidth (str): Minimum width of the question in CSS units.
        noneText (str | None): Text for the 'None' choice.
        otherErrorText (str | None): Error text no text for the 'Other' choice.
        otherText (str | None): Text for the 'Other' choice.
        readOnly (bool): Whether the question is read-only.
        refuseText: str | None = None
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        selectAllText (str | None): Text for the 'Select All' item.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showDontKnowItem (bool): Show don't know option. Defaults to `False`.
        showNoneItem (bool): Show none option. Defaults to `False`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        showRefuseItem (bool): Show refuse option. Defaults to `False`.
        showSelectAllItem (bool | None): Whether to show the 'Select All' item.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "choicesFromQuestion": choicesFromQuestion,
        "choicesFromQuestionMode": choicesFromQuestionMode,
        "choicesOrder": choicesOrder,
        "showDontKnowItem": showDontKnowItem,
        "dontKnowText": dontKnowText,
        "hideIfChoicesEmpty": hideIfChoicesEmpty,
        "showNoneItem": showNoneItem,
        "noneText": noneText,
        "otherText": otherText,
        "otherErrorText": otherErrorText,
        "showRefuseItem": showRefuseItem,
        "refuseText": refuseText,
        "colCount": colCount,
        "isAllSelected": isAllSelected,
        "maxSelectedChoices": maxSelectedChoices,
        "minSelectedChoices": minSelectedChoices,
        "selectAllText": selectAllText,
        "showSelectAllItem": showSelectAllItem,
    }
    choices = flatten(choices)
    if not isinstance(title, list):
        title = [title]
    if len(title) != 1:
        return [
            QuestionCheckboxModel(
                name=f"{name}_{i+1}", title=t, choices=choices, **args, **kwargs
            )
            for i, t in enumerate(title)
        ]
    else:
        return QuestionCheckboxModel(
            name=name, title=title[0], choices=choices, **args, **kwargs
        )


def ranking(
    name: str,
    title: str | list[str] | None,
    *choices: str | dict | list,
    addCode: dict | None = None,
    choicesFromQuestion: str | None = None,
    choicesFromQuestionMode: str = "all",
    choicesOrder: str = "none",
    colCount: int | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    dontKnowText: str | None = None,
    enableIf: str | None = None,
    errorLocation: str = "default",
    hideIfChoicesEmpty: bool | None = None,
    id: str | None = None,
    isAllSelected: bool | None = None,
    isRequired: bool = False,
    longTap: bool = True,
    maxSelectedChoices: int = 0,
    maxWidth: str = "100%",
    minSelectedChoices: int = 0,
    minWidth: str = "300px",
    noneText: str | None = None,
    otherErrorText: str | None = None,
    otherText: str | None = None,
    readOnly: bool = False,
    refuseText: str | None = None,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    selectAllText: str | None = None,
    selectToRankAreasLayout: str = "horizontal",
    selectToRankEmptyRankedAreaText: str | None = None,
    selectToRankEmptyUnrankedAreaText: str | None = None,
    selectToRankEnabled: bool = False,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showDontKnowItem: bool = False,
    showNoneItem: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    showRefuseItem: bool = False,
    showSelectAllItem: bool | None = None,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionRankingModel | list[QuestionRankingModel]:
    """Create a ranking question object

    Args:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        choices (str | dict | list): The choices for the question. Can be string(s) or dictionary(-ies) with structure `{"value": ..., "text": ...}`. You can also add `visibleIf`, `enableIf`, and `requiredIf` to the dictionary.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        choicesFromQuestion (str | None): The name of the question to get the choices from if the are to be copied. Use with `choicesFromQuestionMode`.
        choicesFromQuestionMode (str): The mode of copying choices. Can be 'all', 'selected', 'unselected'.
        choicesOrder (str): The order of the choices. Can be 'none', 'asc', 'desc', 'random'.
        colCount (int | None): The number of columns for the choices. 0 means a single line.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        dontKnowText: str | None = None
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        hideIfChoicesEmpty (bool | None): Whether to hide the question if there are no choices.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isAllSelected (bool | None): Start with all choices selected. Default is False.
        isRequired (bool): Whether the question is required.
        longTap (bool): Whether to use long tap for dragging on mobile devices.
        maxSelectedChoices (int): Maximum number of selected choices. 0 means no limit.
        maxWidth (str): Maximum width of the question in CSS units.
        minSelectedChoices (int): Minimum number of selected choices. 0 means no limit.
        minWidth (str): Minimum width of the question in CSS units.
        noneText (str | None): Text for the 'None' choice.
        otherErrorText (str | None): Error text no text for the 'Other' choice.
        otherText (str | None): Text for the 'Other' choice.
        readOnly (bool): Whether the question is read-only.
        refuseText: str | None = None
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        selectAllText (str | None): Text for the 'Select All' item.
        selectToRankAreasLayout (str): The layout of the ranked and unranked areas when `selectToRankEnabled=True`. Can be 'horizontal', 'vertical'.
        selectToRankEmptyRankedAreaText (str | None): Text for the empty ranked area when `selectToRankEnabled=True`.
        selectToRankEmptyUnrankedAreaText (str | None): Text for the empty unranked area when `selectToRankEnabled=True`.
        selectToRankEnabled (bool): Whether user should select items they want to rank before ranking them. Default is False.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showDontKnowItem (bool): Show don't know option. Defaults to `False`.
        showNoneItem (bool): Show none option. Defaults to `False`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        showRefuseItem (bool): Show refuse option. Defaults to `False`.
        showSelectAllItem (bool | None): Whether to show the 'Select All' item.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "choicesFromQuestion": choicesFromQuestion,
        "choicesFromQuestionMode": choicesFromQuestionMode,
        "choicesOrder": choicesOrder,
        "showDontKnowItem": showDontKnowItem,
        "dontKnowText": dontKnowText,
        "hideIfChoicesEmpty": hideIfChoicesEmpty,
        "showNoneItem": showNoneItem,
        "noneText": noneText,
        "otherText": otherText,
        "otherErrorText": otherErrorText,
        "showRefuseItem": showRefuseItem,
        "refuseText": refuseText,
        "colCount": colCount,
        "isAllSelected": isAllSelected,
        "maxSelectedChoices": maxSelectedChoices,
        "minSelectedChoices": minSelectedChoices,
        "selectAllText": selectAllText,
        "showSelectAllItem": showSelectAllItem,
        "longTap": longTap,
        "selectToRankAreasLayout": selectToRankAreasLayout,
        "selectToRankEmptyRankedAreaText": selectToRankEmptyRankedAreaText,
        "selectToRankEmptyUnrankedAreaText": selectToRankEmptyUnrankedAreaText,
        "selectToRankEnabled": selectToRankEnabled,
    }
    choices = flatten(choices)
    if not isinstance(title, list):
        title = [title]
    if len(title) != 1:
        return [
            QuestionRankingModel(
                name=f"{name}_{i+1}", title=t, choices=choices, **args, **kwargs
            )
            for i, t in enumerate(title)
        ]
    else:
        return QuestionRankingModel(
            name=name, title=title[0], choices=choices, **args, **kwargs
        )


def radio(
    name: str,
    title: str | list[str] | None,
    *choices: str | dict | list,
    addCode: dict | None = None,
    allowClear: bool = False,
    choicesFromQuestion: str | None = None,
    choicesFromQuestionMode: str = "all",
    choicesOrder: str = "none",
    colCount: int | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    dontKnowText: str | None = None,
    enableIf: str | None = None,
    errorLocation: str = "default",
    hideIfChoicesEmpty: bool | None = None,
    id: str | None = None,
    isRequired: bool = False,
    maxWidth: str = "100%",
    minWidth: str = "300px",
    noneText: str | None = None,
    otherErrorText: str | None = None,
    otherText: str | None = None,
    readOnly: bool = False,
    refuseText: str | None = None,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showDontKnowItem: bool = False,
    showNoneItem: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    showRefuseItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionRadiogroupModel | list[QuestionRadiogroupModel]:
    """Create a radio question object

    Args:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        choices (str | dict | list): The choices for the question. Can be string(s) or dictionary(-ies) with structure `{"value": ..., "text": ...}`. You can also add `visibleIf`, `enableIf`, and `requiredIf` to the dictionary.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        allowClear (bool): Show a button to clear the answer.
        choicesFromQuestion (str | None): The name of the question to get the choices from if the are to be copied. Use with `choicesFromQuestionMode`.
        choicesFromQuestionMode (str): The mode of copying choices. Can be 'all', 'selected', 'unselected'.
        choicesOrder (str): The order of the choices. Can be 'none', 'asc', 'desc', 'random'.
        colCount (int | None): The number of columns for the choices. 0 means a single line.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        dontKnowText: str | None = None
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        hideIfChoicesEmpty (bool | None): Whether to hide the question if there are no choices.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isRequired (bool): Whether the question is required.
        maxWidth (str): Maximum width of the question in CSS units.
        minWidth (str): Minimum width of the question in CSS units.
        noneText (str | None): Text for the 'None' choice.
        otherErrorText (str | None): Error text no text for the 'Other' choice.
        otherText (str | None): Text for the 'Other' choice.
        readOnly (bool): Whether the question is read-only.
        refuseText: str | None = None
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showDontKnowItem (bool): Show don't know option. Defaults to `False`.
        showNoneItem (bool): Show none option. Defaults to `False`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        showRefuseItem (bool): Show refuse option. Defaults to `False`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.

    Returns:
        QuestionRadiogroupModel: The question object model or a list of question object models if `title` is a list.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "choicesFromQuestion": choicesFromQuestion,
        "choicesFromQuestionMode": choicesFromQuestionMode,
        "choicesOrder": choicesOrder,
        "showDontKnowItem": showDontKnowItem,
        "dontKnowText": dontKnowText,
        "hideIfChoicesEmpty": hideIfChoicesEmpty,
        "showNoneItem": showNoneItem,
        "noneText": noneText,
        "otherText": otherText,
        "otherErrorText": otherErrorText,
        "showRefuseItem": showRefuseItem,
        "refuseText": refuseText,
        "colCount": colCount,
        "allowClear": allowClear,
    }
    choices = flatten(choices)
    if not isinstance(title, list):
        title = [title]
    if len(title) != 1:
        return [
            QuestionRadiogroupModel(
                name=f"{name}_{i+1}", title=t, choices=choices, **args, **kwargs
            )
            for i, t in enumerate(title)
        ]
    else:
        return QuestionRadiogroupModel(
            name=name, title=title[0], choices=choices, **args, **kwargs
        )


def dropdownMultiple(
    name: str,
    title: str | list[str] | None,
    *choices: str | dict | list,
    addCode: dict | None = None,
    allowClear: bool = True,
    choicesFromQuestion: str | None = None,
    choicesFromQuestionMode: str = "all",
    choicesOrder: str = "none",
    closeOnSelect: int | None = None,
    colCount: int | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    dontKnowText: str | None = None,
    enableIf: str | None = None,
    errorLocation: str = "default",
    hideIfChoicesEmpty: bool | None = None,
    hideSelectedItems: bool | None = False,
    id: str | None = None,
    isAllSelected: bool | None = None,
    isRequired: bool = False,
    maxSelectedChoices: int = 0,
    maxWidth: str = "100%",
    minSelectedChoices: int = 0,
    minWidth: str = "300px",
    noneText: str | None = None,
    otherErrorText: str | None = None,
    otherText: str | None = None,
    placeholder: str | None = None,
    readOnly: bool = False,
    refuseText: str | None = None,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    searchEnabled: bool = True,
    searchMode: str = "contains",
    selectAllText: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showDontKnowItem: bool = False,
    showNoneItem: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    showRefuseItem: bool = False,
    showSelectAllItem: bool | None = None,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionTagboxModel | list[QuestionTagboxModel]:
    """Create a multiple dropdown question object

    Args:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        choices (str | dict | list): The choices for the question. Can be string(s) or dictionary(-ies) with structure `{"value": ..., "text": ...}`. You can also add `visibleIf`, `enableIf`, and `requiredIf` to the dictionary.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        allowClear (str): Whether to show the 'Clear' button for each answer.
        choicesFromQuestion (str | None): The name of the question to get the choices from if the are to be copied. Use with `choicesFromQuestionMode`.
        choicesFromQuestionMode (str): The mode of copying choices. Can be 'all', 'selected', 'unselected'.
        choicesOrder (str): The order of the choices. Can be 'none', 'asc', 'desc', 'random'.
        closeOnSelect (int | None): Whether to close the dropdown after user selects a specified number of items.
        colCount (int | None): The number of columns for the choices. 0 means a single line.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        dontKnowText: str | None = None
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        hideIfChoicesEmpty (bool | None): Whether to hide the question if there are no choices.
        hideSelectedItems (bool | None): Whether to hide selected items in the dropdown.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isAllSelected (bool | None): Start with all choices selected. Default is False.
        isRequired (bool): Whether the question is required.
        maxSelectedChoices (int): Maximum number of selected choices. 0 means no limit.
        maxWidth (str): Maximum width of the question in CSS units.
        minSelectedChoices (int): Minimum number of selected choices. 0 means no limit.
        minWidth (str): Minimum width of the question in CSS units.
        noneText (str | None): Text for the 'None' choice.
        otherErrorText (str | None): Error text no text for the 'Other' choice.
        otherText (str | None): Text for the 'Other' choice.
        placeholder (str | None): Placeholder text for the input with no value.
        readOnly (bool): Whether the question is read-only.
        refuseText: str | None = None
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        searchEnabled (bool): Whether to enable search in the dropdown.
        searchMode (str): The search mode. Can be 'contains' (default), 'startsWith'. Works only if `searchEnabled=True`.
        selectAllText (str | None): Text for the 'Select All' item.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showDontKnowItem (bool): Show don't know option. Defaults to `False`.
        showNoneItem (bool): Show none option. Defaults to `False`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        showRefuseItem (bool): Show refuse option. Defaults to `False`.
        showSelectAllItem (bool | None): Whether to show the 'Select All' item.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "choicesFromQuestion": choicesFromQuestion,
        "choicesFromQuestionMode": choicesFromQuestionMode,
        "choicesOrder": choicesOrder,
        "showDontKnowItem": showDontKnowItem,
        "dontKnowText": dontKnowText,
        "hideIfChoicesEmpty": hideIfChoicesEmpty,
        "showNoneItem": showNoneItem,
        "noneText": noneText,
        "otherText": otherText,
        "otherErrorText": otherErrorText,
        "showRefuseItem": showRefuseItem,
        "refuseText": refuseText,
        "colCount": colCount,
        "isAllSelected": isAllSelected,
        "maxSelectedChoices": maxSelectedChoices,
        "minSelectedChoices": minSelectedChoices,
        "selectAllText": selectAllText,
        "showSelectAllItem": showSelectAllItem,
        "allowClear": allowClear,
        "closeOnSelect": closeOnSelect,
        "hideSelectedItems": hideSelectedItems,
        "placeholder": placeholder,
        "searchEnabled": searchEnabled,
        "searchMode": searchMode,
    }
    choices = flatten(choices)
    if not isinstance(title, list):
        title = [title]
    if len(title) != 1:
        return [
            QuestionTagboxModel(
                name=f"{name}_{i+1}", title=t, choices=choices, **args, **kwargs
            )
            for i, t in enumerate(title)
        ]
    else:
        return QuestionTagboxModel(
            name=name, title=title[0], choices=choices, **args, **kwargs
        )


def textLong(
    name: str,
    *title: str | list[str] | None,
    acceptCarriageReturn: bool = True,
    addCode: dict | None = None,
    allowResize: bool | None = None,
    autoGrow: bool | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    enableIf: str | None = None,
    errorLocation: str = "default",
    id: str | None = None,
    isRequired: bool = False,
    maxWidth: str = "100%",
    minWidth: str = "300px",
    monitorInput: bool = False,
    readOnly: bool = False,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    rows: int = 4,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionCommentModel | list[QuestionCommentModel]:
    """Create a long text question object

    Attributes:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        acceptCarriageReturn (bool): Whether to allow line breaks. Default is True.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        allowResize (bool): Whether to allow resizing the input field. Default is True.
        autoGrow (bool): Whether to automatically grow the input field. Default is False.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isRequired (bool): Whether the question is required.
        maxWidth (str): Maximum width of the question in CSS units.
        minWidth (str): Minimum width of the question in CSS units.
        monitorInput (bool): Whether to count the time spent with the question focused and the number of key presses. Useful for bot detection.
        readOnly (bool): Whether the question is read-only.
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        rows (int): Height of the input field in rows' number.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "monitorInput": monitorInput,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "acceptCarriageReturn": acceptCarriageReturn,
        "allowResize": allowResize,
        "autoGrow": autoGrow,
        "rows": rows,
    }
    title = flatten(title)
    if len(title) != 1:
        return [
            QuestionCommentModel(name=f"{name}_{i+1}", title=t, **args, **kwargs)
            for i, t in enumerate(title)
        ]
    return QuestionCommentModel(name=name, title=title[0], **args, **kwargs)


def rating(
    name: str,
    *title: str | list[str] | None,
    addCode: dict | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    enableIf: str | None = None,
    errorLocation: str = "default",
    id: str | None = None,
    isRequired: bool = False,
    maxRateDescription: str | None = None,
    maxWidth: str = "100%",
    minRateDescription: str | None = None,
    minWidth: str = "300px",
    rateMax: int = 5,
    rateMin: int = 1,
    rateStep: int = 1,
    rateType: str = "labels",
    rateValues: list | None = None,
    readOnly: bool = False,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    scaleColorMode: str = "monochrome",
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionRatingModel | list[QuestionRatingModel]:
    """Create a rating question object

    Attributes:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isRequired (bool): Whether the question is required.
        maxRateDescription (str | None): Description for the biggest rate.
        maxWidth (str): Maximum width of the question in CSS units.
        minRateDescription (str | None): Description for the smallest rate.
        minWidth (str): Minimum width of the question in CSS units.
        rateMax (int): Maximum rate. Works only if `rateValues` is not set.
        rateMin (int): Minimum rate. Works only if `rateValues` is not set.
        rateStep (int): Step for the rate. Works only if `rateValues` is not set.
        rateType (str): The type of the rate. Can be 'labels', 'stars', 'smileys'.
        rateValues (list | None): Manually set rate values. Use a list of primitives and/or dictionaries `{"value": ..., "text": ...}`.
        readOnly (bool): Whether the question is read-only.
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        scaleColorMode (str): The color mode of the scale if `rateType='smileys'`. Can be 'monochrome', 'colored'.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "maxRateDescription": maxRateDescription,
        "minRateDescription": minRateDescription,
        "rateMax": rateMax,
        "rateMin": rateMin,
        "rateStep": rateStep,
        "rateType": rateType,
        "rateValues": rateValues,
        "scaleColorMode": scaleColorMode,
    }
    title = flatten(title)
    if len(title) != 1:
        return [
            QuestionRatingModel(name=f"{name}_{i+1}", title=t, **args, **kwargs)
            for i, t in enumerate(title)
        ]
    return QuestionRatingModel(name=name, title=title[0], **args, **kwargs)


def yesno(
    name: str,
    *title: str | list[str] | None,
    addCode: dict | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    enableIf: str | None = None,
    errorLocation: str = "default",
    id: str | None = None,
    isRequired: bool = False,
    labelFalse: str | None = None,
    labelTrue: str | None = None,
    maxWidth: str = "100%",
    minWidth: str = "300px",
    readOnly: bool = False,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    swapOrder: bool = False,
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    valueFalse: bool | str = False,
    valueTrue: bool | str = True,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionBooleanModel | list[QuestionBooleanModel]:
    """Create a yes/no (boolean) question object

    Attributes:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isRequired (bool): Whether the question is required.
        labelFalse (str | None): Label for the 'false' value.
        labelTrue (str | None): Label for the 'true' value.
        maxWidth (str): Maximum width of the question in CSS units.
        minWidth (str): Minimum width of the question in CSS units.
        readOnly (bool): Whether the question is read-only.
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        swapOrder (bool): Whether to swap the default (no, yes) order of the labels.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        valueFalse (str): Value for the 'false' option.
        valueTrue (str): Value for the 'true' option.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "labelFalse": labelFalse,
        "labelTrue": labelTrue,
        "swapOrder": swapOrder,
        "valueFalse": valueFalse,
        "valueTrue": valueTrue,
    }
    title = flatten(title)
    if len(title) != 1:
        return [
            QuestionBooleanModel(name=f"{name}_{i+1}", title=t, **args, **kwargs)
            for i, t in enumerate(title)
        ]
    return QuestionBooleanModel(name=name, title=title[0], **args, **kwargs)


def info(
    name: str,
    *infoHTML: str | list[str],
    addCode: dict | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    enableIf: str | None = None,
    errorLocation: str = "default",
    id: str | None = None,
    isRequired: bool = False,
    maxWidth: str = "100%",
    minWidth: str = "300px",
    readOnly: bool = False,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionHtmlModel | list[QuestionHtmlModel]:
    """Create an informational text object

    Args:
        name (str): The label of the question.
        infoHTML (str): The HTML content of the infobox.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isRequired (bool): Whether the question is required.
        maxWidth (str): Maximum width of the question in CSS units.
        minWidth (str): Minimum width of the question in CSS units.
        readOnly (bool): Whether the question is read-only.
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        title (str | None): The visible title of the question. If None, `name` is used.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
        addCode (dict | None): Additional code for the question. Usually not necessary.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
    }
    infoHTML = flatten(infoHTML)
    if len(infoHTML) != 1:
        return [
            QuestionHtmlModel(name=f"{name}_{i+1}", html=html, **args, **kwargs)
            for i, html in enumerate(infoHTML)
        ]
    return QuestionHtmlModel(name=name, html=infoHTML[0], **args, **kwargs)


def matrix(
    name: str,
    title: str | list[str] | None,
    columns: list | dict,
    *rows: list | dict,
    addCode: dict | None = None,
    alternateRows: bool | None = None,
    columnMinWidth: str | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    displayMode: str = "auto",
    eachRowRequired: bool = False,
    eachRowUnique: bool | None = None,
    enableIf: str | None = None,
    errorLocation: str = "default",
    hideIfRowsEmpty: bool | None = None,
    id: str | None = None,
    isRequired: bool = False,
    maxWidth: str = "100%",
    minWidth: str = "300px",
    readOnly: bool = False,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    rowOrder: str = "initial",
    rowTitleWidth: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showHeader: bool = True,
    showNumber: bool = False,
    showOtherItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    verticalAlign: str = "middle",
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionMatrixModel | list[QuestionMatrixModel]:
    """Create a matrix question object

    Attributes:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        columns (list | dict): The columns of the matrix. Use primitives or dictionaries `{"text": ..., "value": ..., "otherParameter": ...}`.
        rows (list | dict): The rows of the matrix. Use primitives or dictionaries `{"text": ..., "value": ..., "otherParameter": ...}`.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        alternateRows (bool | None): Whether to alternate the rows.
        columnMinWidth (str | None): Minimum width of the column in CSS units.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        displayMode (str): The display mode of the matrix. Can be 'auto', 'list', 'table'.
        eachRowRequired (bool): Whether each and every row is to be required.
        eachRowUnique (bool | None): Whether each row should have a unique answer. Defaults to False.
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        hideIfRowsEmpty (bool | None): Whether to hide the question if no rows are visible.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isRequired (bool): Whether the question is required.
        maxWidth (str): Maximum width of the question in CSS units.
        minWidth (str): Minimum width of the question in CSS units.
        readOnly (bool): Whether the question is read-only.
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        rowOrder (str): The order of the rows. Can be 'initial', 'random'.
        rowTitleWidth (str | None): Width of the row title in CSS units. If you want to make the row title bigger compared to the answer columns, also set `columnMinWidth` to a smaller value in px or percentage.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showHeader (bool): Whether to show the header of the table.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        verticalAlign (str): The vertical alignment of the content. Can be 'top', 'middle'.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "alternateRows": alternateRows,
        "columnMinWidth": columnMinWidth,
        "displayMode": displayMode,
        "rowTitleWidth": rowTitleWidth,
        "showHeader": showHeader,
        "verticalAlign": verticalAlign,
        "eachRowUnique": eachRowUnique,
        "hideIfRowsEmpty": hideIfRowsEmpty,
        "eachRowRequired": eachRowRequired,
        "rowOrder": rowOrder,
    }
    rows = flatten(rows)
    if not isinstance(title, list):
        title = [title]
    rows_changed = []
    for i, row in enumerate(rows):
        if isinstance(row, dict):
            rows_changed.append(row)
        else:
            rows_changed.append({"value": f"{name}_{i+1}", "text": row})
    if len(title) != 1:
        return [
            QuestionMatrixModel(
                name=f"{name}_{i+1}",
                title=t,
                columns=columns,
                rows=rows_changed,
                **args,
                **kwargs,
            )
            for i, t in enumerate(title)
        ]
    return QuestionMatrixModel(
        name=name, title=title[0], columns=columns, rows=rows_changed, **args, **kwargs
    )


def matrixDropdown(
    name: str,
    title: str | list[str],
    columns: list | QuestionModel | dict,
    *rows: list | dict,
    addCode: dict | None = None,
    alternateRows: bool | None = None,
    cellErrorLocation: str = "default",
    cellType: str | None = None,
    columnMinWidth: str | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    customCode: str | None = None,
    customFunctions: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    displayMode: str = "auto",
    enableIf: str | None = None,
    errorLocation: str = "default",
    id: str | None = None,
    isRequired: bool = False,
    maxWidth: str = "100%",
    minWidth: str = "300px",
    placeHolder: str | None = None,
    readOnly: bool = False,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    rowTitleWidth: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showHeader: bool = True,
    showNumber: bool = False,
    showOtherItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    transposeData: bool = False,
    useCaseSensitiveComparison: bool = False,
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    verticalAlign: str = "middle",
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
):
    """Create a matrix, where each column can be a question of a specified type.

    Args:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        columns (list | QuestionModel | dict): The columns of the matrix. Use question objects or dictionaries.
        rows (list | dict): The rows of the matrix. Use primitives or dictionaries `{"text": ..., "value": ..., "otherParameter": ...}`.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        alternateRows (bool | None): Whether to alternate the rows.
        cellErrorLocation (str): The location of the error text for the cells. Can be 'default', 'top', 'bottom'.
        cellType (str | None): The type of the matrix cells. Can be overridden for individual columns. Can be "dropdown" (default), "checkbox", "radiogroup", "tagbox", "text", "comment", "boolean", "expression", "rating".
        choices (str | dict | list | None): The default choices for all select questions. Can be overridden for individual columns. Can be string(s) or dictionary(-ies) with structure `{"value": ..., "text": ..., "otherParameter": ...}`.
        columnMinWidth (str | None): Minimum width of the column in CSS units.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        displayMode (str): The display mode of the matrix. Can be 'auto', 'list', 'table'.
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isRequired (bool): Whether the question is required.
        maxWidth (str): Maximum width of the question in CSS units.
        minWidth (str): Minimum width of the question in CSS units.
        placeHolder (str | None): Placeholder text for the cells.
        readOnly (bool): Whether the question is read-only.
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        rowTitleWidth (str | None): Width of the row title in CSS units. If you want to make the row title bigger compared to the answer columns, also set `columnMinWidth` to a smaller value in px or percentage.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showHeader (bool): Whether to show the header of the table.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        transposeData (bool): Whether to show columns as rows. Default is False.
        useCaseSensitiveComparison (bool): Whether the case of the answer should be considered when checking for uniqueness. If `True`, "Kowalski" and "kowalski" will be considered different answers.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        verticalAlign (str): The vertical alignment of the content. Can be 'top', 'middle'.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "customCode": customCode,
        "customFunctions": customFunctions,
        "alternateRows": alternateRows,
        "columnMinWidth": columnMinWidth,
        "displayMode": displayMode,
        "rowTitleWidth": rowTitleWidth,
        "showHeader": showHeader,
        "verticalAlign": verticalAlign,
        "cellErrorLocation": cellErrorLocation,
        "cellType": cellType,
        "useCaseSensitiveComparison": useCaseSensitiveComparison,
        "placeHolder": placeHolder,
        "transposeData": transposeData,
    }
    rows = flatten(rows)
    if not isinstance(title, list):
        title = [title]
    if not isinstance(columns, list):
        columns = [columns]
    rows_changed = []
    for i, row in enumerate(rows):
        if isinstance(row, dict):
            rows_changed.append(row)
        else:
            rows_changed.append({"value": f"{name}_{i+1}", "text": row})
    if len(title) != 1:
        return [
            QuestionMatrixDropdownModel(
                name=f"{name}_{i+1}",
                title=t,
                columns=columns,
                rows=rows_changed,
                **args,
                **kwargs,
            )
            for i, t in enumerate(title)
        ]
    return QuestionMatrixDropdownModel(
        name=name, title=title[0], columns=columns, rows=rows_changed, **args, **kwargs
    )


def matrixDynamic(
    name: str,
    title: str | list[str] | None,
    *columns,
    addCode: dict | None = None,
    addRowButtonLocation: str = "default",
    addRowText: str | None = None,
    allowAddRows: bool = True,
    allowRemoveRows: bool = True,
    allowRowReorder: bool = False,
    alternateRows: bool | None = None,
    cellErrorLocation: str = "default",
    cellType: str | None = None,
    columnMinWidth: str | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    confirmDelete: bool = False,
    confirmDeleteText: str | None = None,
    copyDefaultValueFromLastEntry: bool = False,
    correctAnswer: str | None = None,
    defaultRowValue: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    displayMode: str = "auto",
    enableIf: str | None = None,
    errorLocation: str = "default",
    hideColumnsIfEmpty: bool = False,
    id: str | None = None,
    isRequired: bool = False,
    maxRowCount: int = 1000,
    maxWidth: str = "100%",
    minRowCount: int = 0,
    minWidth: str = "300px",
    noRowsText: str | None = None,
    placeHolder: str | None = None,
    readOnly: bool = False,
    removeRowText: str | None = None,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    rowCount: int = 2,
    rowTitleWidth: str | None = None,
    rows: list | dict | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showHeader: bool = True,
    showNumber: bool = False,
    showOtherItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    transposeData: bool = False,
    useCaseSensitiveComparison: bool = False,
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    verticalAlign: str = "middle",
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionMatrixDynamicModel | list[QuestionMatrixDynamicModel]:
    """Create a dynamic matrix question object

    Attributes:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        columns (list | dict): The columns of the matrix. Use primitives or dictionaries `{"text": ..., "value": ..., "type": ..., "otherParameter": ...}`.
        rows (list | dict): The rows of the matrix. Use primitives or dictionaries `{"text": ..., "value": ..., "otherParameter": ...}`.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        addRowButtonLocation (str): The location of the 'Add row' button. Can be 'default', 'top', 'bottom', 'topBottom' (both top and bottom).
        addRowText (str | None): Text for the 'Add row' button.
        allowAddRows (bool): Whether to allow adding rows.
        allowRemoveRows (bool): Whether to allow removing rows.
        allowRowReorder (bool): Whether to allow dragging and dropping rows to change order.
        alternateRows (bool | None): Whether to alternate the rows.
        cellErrorLocation (str): The location of the error text for the cells. Can be 'default', 'top', 'bottom'.
        cellType (str | None): The type of the matrix cells. Can be overridden for individual columns. Can be "dropdown" (default), "checkbox", "radiogroup", "tagbox", "text", "comment", "boolean", "expression", "rating".
        choices (str | dict | list): The default choices for all select questions. Can be overridden for individual columns. Can be string(s) or dictionary(-ies) with structure `{"value": ..., "text": ..., "otherParameter": ...}`.
        columnMinWidth (str | None): Minimum width of the column in CSS units.
        columns (list | dict): The columns of the matrix. Use primitives or dictionaries `{"text": ..., "value": ..., "type": ..., "otherParameter": ...}`.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        confirmDelete (bool): Whether to prompt for confirmation before deleting a row. Default is False.
        confirmDeleteText (str | None): Text for the confirmation dialog when `confirmDelete` is True.
        copyDefaultValueFromLastEntry (bool): Whether to copy the value from the last row to the new row.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultRowValue (str | None): Default value for the new rows that has no `defaultValue` property.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        displayMode (str): The display mode of the matrix. Can be 'auto', 'list', 'table'.
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        hideColumnsIfEmpty (bool): Whether to hide columns if there are no rows.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        isRequired (bool): Whether the question is required.
        maxRowCount (int): Maximum number of rows.
        maxWidth (str): Maximum width of the question in CSS units.
        minRowCount (int): Minimum number of rows.
        minWidth (str): Minimum width of the question in CSS units.
        noRowsText (str | None): Text to display when there are no rows if `hideColumnsIfEmpty` is True.
        placeHolder (str | None): Placeholder text for the cells.
        readOnly (bool): Whether the question is read-only.
        removeRowText (str | None): Text for the 'Remove row' button.
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        rowCount (int): The initial number of rows.
        rowTitleWidth (str | None): Width of the row title in CSS units. If you want to make the row title bigger compared to the answer columns, also set `columnMinWidth` to a smaller value in px or percentage.
        rows (list | dict): The rows of the matrix. Use primitives or dictionaries `{"text": ..., "value": ...}`.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showHeader (bool): Whether to show the header of the table.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        transposeData (bool): Whether to show columns as rows. Default is False.
        useCaseSensitiveComparison (bool): Whether the case of the answer should be considered when checking for uniqueness. If `True`, "Kowalski" and "kowalski" will be considered different answers.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        verticalAlign (str): The vertical alignment of the content. Can be 'top', 'middle'.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "rows": rows,
        "alternateRows": alternateRows,
        "columnMinWidth": columnMinWidth,
        "displayMode": displayMode,
        "rowTitleWidth": rowTitleWidth,
        "showHeader": showHeader,
        "verticalAlign": verticalAlign,
        "cellErrorLocation": cellErrorLocation,
        "cellType": cellType,
        "useCaseSensitiveComparison": useCaseSensitiveComparison,
        "placeHolder": placeHolder,
        "transposeData": transposeData,
        "addRowButtonLocation": addRowButtonLocation,
        "addRowText": addRowText,
        "allowAddRows": allowAddRows,
        "allowRemoveRows": allowRemoveRows,
        "allowRowReorder": allowRowReorder,
        "confirmDelete": confirmDelete,
        "confirmDeleteText": confirmDeleteText,
        "defaultRowValue": defaultRowValue,
        "copyDefaultValueFromLastEntry": copyDefaultValueFromLastEntry,
        "noRowsText": noRowsText,
        "hideColumnsIfEmpty": hideColumnsIfEmpty,
        "maxRowCount": maxRowCount,
        "minRowCount": minRowCount,
        "removeRowText": removeRowText,
        "rowCount": rowCount,
    }
    columns = flatten(columns)
    if not isinstance(title, list):
        title = [title]
    if len(title) != 1:
        return [
            QuestionMatrixDynamicModel(
                name=f"{name}_{i+1}", title=t, columns=columns, **args, **kwargs
            )
            for i, t in enumerate(title)
        ]
    return QuestionMatrixDynamicModel(
        name=name, title=title[0], columns=columns, **args, **kwargs
    )


def slider(
    name: str,
    *title: str | list[str] | None,
    addCode: dict | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    direction: str = "ltr",
    enableIf: str | None = None,
    errorLocation: str = "default",
    id: str | None = None,
    isRequired: bool = False,
    maxWidth: str = "100%",
    minWidth: str = "300px",
    orientation: str = "horizontal",
    pipsDensity: int = 5,
    pipsMode: str = "positions",
    pipsText: list = [0, 25, 50, 75, 100],
    pipsValues: list = [0, 25, 50, 75, 100],
    rangeMax: int = 100,
    rangeMin: int = 0,
    readOnly: bool = False,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    step: int = 1,
    titleLocation: str = "default",
    tooltips: bool = True,
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionNoUiSliderModel | list[QuestionNoUiSliderModel]:
    """Create a slider question object

    Args:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        direction (str): The direction of the slider. Can be 'ltr', 'rtl'.
        orientation (str): The orientation of the slider. Can be 'horizontal', 'vertical'.
        pipsDensity (int): The density of the pips.
        pipsMode (str): The mode of the pips. Can be 'positions', 'values', 'count', 'range', 'steps'. See <https://refreshless.com/nouislider/pips/>
        pipsText (list): The text of the pips.
        pipsValues (list): The values of the pips.
        rangeMax (int): The maximum value of the slider.
        rangeMin (int): The minimum value of the slider.
        step (int): The step of the slider.
        tooltips (bool): Whether to show tooltips.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "step": step,
        "rangeMin": rangeMin,
        "rangeMax": rangeMax,
        "pipsMode": pipsMode,
        "pipsValues": pipsValues,
        "pipsText": pipsText,
        "pipsDensity": pipsDensity,
        "orientation": orientation,
        "direction": direction,
        "tooltips": tooltips,
    }
    title = flatten(title)
    if len(title) != 1:
        return [
            QuestionNoUiSliderModel(name=f"{name}_{i+1}", title=t, **args, **kwargs)
            for i, t in enumerate(title)
        ]
    return QuestionNoUiSliderModel(name=name, title=title[0], **args, **kwargs)


def image(
    name: str,
    *imageLink: str,
    addCode: dict | None = None,
    altText: str | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    contentMode: str = "auto",
    correctAnswer: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    enableIf: str | None = None,
    errorLocation: str = "default",
    id: str | None = None,
    imageFit: str = "contain",
    imageHeight: int | str = 150,
    imageWidth: int | str = 200,
    isRequired: bool = False,
    maxWidth: str = "100%",
    minWidth: str = "300px",
    readOnly: bool = False,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionImageModel | list[QuestionImageModel]:
    """An image or video question object

    Args:
        name (str): The label of the question.
        imageLink (str | None): The src property for <img> or video link.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        altText (str | None): The alt property for <img>.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        contentMode (str): The content type. Can be 'auto' (default), 'image', 'video', 'youtube'.
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        imageFit (str): The object-fit property of <img>. Can be 'contain', 'cover', 'fill', 'none'. See MDN <https://developer.mozilla.org/en-US/docs/Web/CSS/object-fit>.
        imageHeight (int | str): The height of the image container in CSS units. See `imageFit`.
        imageWidth (int | str): The width of the image container in CSS units. See `imageFit`.
        isRequired (bool): Whether the question is required.
        maxWidth (str): Maximum width of the question in CSS units.
        minWidth (str): Minimum width of the question in CSS units.
        readOnly (bool): Whether the question is read-only.
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        title (str | None): The visible title of the question. If None, `name` is used.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units.
    """
    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "altText": altText,
        "contentMode": contentMode,
        "imageFit": imageFit,
        "imageHeight": imageHeight,
        "imageWidth": imageWidth,
    }

    imageLink = flatten(imageLink)
    if len(imageLink) != 1:
        return [
            QuestionImageModel(
                name=f"{name}_{i+1}", imageLink=imageLink, **args, **kwargs
            )
            for i, imageLink in enumerate(imageLink)
        ]
    return QuestionImageModel(name=name, imageLink=imageLink[0], **args, **kwargs)


def imagePicker(
    name: str,
    title: str | list[str] | None,
    *choices: str | dict | list,
    addCode: dict | None = None,
    choicesFromQuestion: str | None = None,
    choicesFromQuestionMode: str = "all",
    choicesOrder: str = "none",
    colCount: int | None = None,
    commentPlaceholder: str | None = None,
    commentText: str | None = None,
    contentMode: str = "image",
    correctAnswer: str | None = None,
    customCode: str | None = None,
    customFunctions: str | None = None,
    defaultValue: str | None = None,
    defaultValueExpression: str | None = None,
    description: str | None = None,
    descriptionLocation: str = "default",
    dontKnowText: str | None = None,
    enableIf: str | None = None,
    errorLocation: str = "default",
    hideIfChoicesEmpty: bool | None = None,
    id: str | None = None,
    imageFit: str = "contain",
    imageHeight: int | str = "auto",
    imageWidth: int | str = "auto",
    isRequired: bool = False,
    maxImageHeight: int | str = 3000,
    maxImageWidth: int | str = 3000,
    maxWidth: str = "100%",
    minImageHeight: int | str = 133,
    minImageWidth: int | str = 200,
    minWidth: str = "300px",
    multiSelect: bool = False,
    noneText: str | None = None,
    otherErrorText: str | None = None,
    otherText: str | None = None,
    readOnly: bool = False,
    refuseText: str | None = None,
    requiredErrorText: str | None = None,
    requiredIf: str | None = None,
    resetValueIf: str | None = None,
    setValueExpression: str | None = None,
    setValueIf: str | None = None,
    showCommentArea: bool = False,
    showDontKnowItem: bool = False,
    showLabel: bool = False,
    showNoneItem: bool = False,
    showNumber: bool = False,
    showOtherItem: bool = False,
    showRefuseItem: bool = False,
    startWithNewLine: bool = True,
    state: str = "default",
    titleLocation: str = "default",
    useDisplayValuesInDynamicTexts: bool = True,
    validators: ValidatorModel | list[ValidatorModel] | None = None,
    visible: bool = True,
    visibleIf: str | None = None,
    width: str = "",
    **kwargs,
) -> QuestionImagePickerModel | list[QuestionImagePickerModel]:
    """Image Picker question object. Use `imageLink` property in the choices' dict to set the image.

    Args:
        name (str): The label of the question.
        title (str | None): The visible title of the question. If None, `name` is used.
        choices (str | dict | list): The choices of the question. Use primitives or dictionaries `{"value": ..., "text": ..., "imageLink": ..., "otherParameter": ...}`.
        addCode (dict | None): Additional code for the question. Usually not necessary.
        choicesFromQuestion (str | None): The name of the question to get the choices from if the are to be copied. Use with `choicesFromQuestionMode`.
        choicesFromQuestionMode (str): The mode of copying choices. Can be 'all', 'selected', 'unselected'.
        choicesOrder (str): The order of the choices. Can be 'none', 'asc', 'desc', 'random'.
        colCount (int | None): The number of columns for the choices. 0 means a single line.
        commentPlaceholder (str | None): Placeholder text for the comment area.
        commentText (str | None): Text for the comment area.
        contentMode (str): Type of content. Can be "image" (default) or "video".
        correctAnswer (str | None): Correct answer for the question. Use for quizzes.
        customCode (str | None): Custom JS commands to be added to the survey.
        customFunctions (str | None): Custom JS functions definitions to be added to the survey. To be used with `customCode`.
        defaultValue (str | None): Default value for the question.
        defaultValueExpression (str | None): Expression deciding the default value for the question.
        description (str | None): Optional subtitle or description of the question.
        descriptionLocation (str): The location of the description. Can be 'default', 'underTitle', 'underInput'.
        dontKnowText: str | None = None
        enableIf (str | None): Expression to enable the question.
        errorLocation (str | None): Location of the error text. Can be 'default' 'top', 'bottom'.
        hideIfChoicesEmpty (bool | None): Whether to hide the question if there are no choices.
        id (str | None): HTML id attribute for the question. Usually not necessary.
        imageFit (str): The object-fit property of the choices. Can be 'contain' (default), 'cover', 'fill', 'none'. See MDN <https://developer.mozilla.org/en-US/docs/Web/CSS/object-fit>.
        imageHeight (int | str): The height of the image container in CSS units. Defaults to "auto".
        imageWidth (int | str): The width of the image container in CSS units. Defaults to "auto".
        isRequired (bool): Whether the question is required.
        maxImageHeight (int | str): The maximum height of the image in CSS units. Defaults to 3000.
        maxImageWidth (int | str): The maximum width of the image in CSS units. Defaults to 3000.
        maxWidth (str): Maximum width of the question in CSS units.
        minImageHeight (int | str): The minimum height of the image in CSS units. Defaults to 133.
        minImageWidth (int | str): The minimum width of the image in CSS units. Defaults to 200.
        minWidth (str): Minimum width of the question in CSS units.
        multiSelect (bool): Whether to allow multiple choices. Default is False.
        noneText (str | None): Text for the 'None' choice.
        otherErrorText (str | None): Error text no text for the 'Other' choice.
        otherText (str | None): Text for the 'Other' choice.
        readOnly (bool): Whether the question is read-only.
        refuseText: str | None = None
        requiredErrorText (str | None): Error text if the required condition is not met.
        requiredIf (str | None): Expression to make the question required.
        resetValueIf (str | None): Expression to reset the value of the question.
        setValueExpression (str | None): Expression to decide on the value of the question to be set. Requires `setValueIf`.
        setValueIf (str | None): Expression with a condition to set the value of the question. Requires `setValueExpression`.
        showCommentArea (bool): Whether to show the comment area. Doesn't work with `showOtherItem`.
        showDontKnowItem (bool): Show don't know option. Defaults to `False`.
        showLabel (bool): Whether to show the label under the image. It is taken from `text` property of the choices. Default is False.
        showNoneItem (bool): Show none option. Defaults to `False`.
        showNumber (bool): Whether to hide the question number.
        showOtherItem (bool): Whether to show the 'Other' item. Doesn't work with `showCommentArea`.
        showRefuseItem (bool): Show refuse option. Defaults to `False`.
        startWithNewLine (bool): Whether to start the question on a new line.
        state (str | None): If the question should be collapsed or expanded. Can be 'default', 'collapsed', 'expanded'.
        titleLocation (str): The location of the title. Can be 'default', 'top', 'bottom', 'left', 'hidden'.
        useDisplayValuesInDynamicTexts (bool): Whether to use display names for question values in placeholders.
        validators (ValidatorModel | list[ValidatorModel] | None): Validator(s) for the question.
        visible (bool): Whether the question is visible.
        visibleIf (str | None): Expression to make the question visible.
        width (str): Width of the question in CSS units."""

    args = {
        "titleLocation": titleLocation,
        "description": description,
        "descriptionLocation": descriptionLocation,
        "isRequired": isRequired,
        "readOnly": readOnly,
        "visible": visible,
        "requiredIf": requiredIf,
        "enableIf": enableIf,
        "visibleIf": visibleIf,
        "validators": validators,
        "showOtherItem": showOtherItem,
        "showCommentArea": showCommentArea,
        "commentPlaceholder": commentPlaceholder,
        "commentText": commentText,
        "correctAnswer": correctAnswer,
        "defaultValue": defaultValue,
        "defaultValueExpression": defaultValueExpression,
        "requiredErrorText": requiredErrorText,
        "errorLocation": errorLocation,
        "showNumber": showNumber,
        "id": id,
        "maxWidth": maxWidth,
        "minWidth": minWidth,
        "resetValueIf": resetValueIf,
        "setValueIf": setValueIf,
        "setValueExpression": setValueExpression,
        "startWithNewLine": startWithNewLine,
        "state": state,
        "useDisplayValuesInDynamicTexts": useDisplayValuesInDynamicTexts,
        "width": width,
        "addCode": addCode,
        "customCode": customCode,
        "customFunctions": customFunctions,
        "choicesFromQuestion": choicesFromQuestion,
        "choicesFromQuestionMode": choicesFromQuestionMode,
        "choicesOrder": choicesOrder,
        "showDontKnowItem": showDontKnowItem,
        "dontKnowText": dontKnowText,
        "hideIfChoicesEmpty": hideIfChoicesEmpty,
        "showNoneItem": showNoneItem,
        "noneText": noneText,
        "otherText": otherText,
        "otherErrorText": otherErrorText,
        "showRefuseItem": showRefuseItem,
        "refuseText": refuseText,
        "colCount": colCount,
        "contentMode": contentMode,
        "imageFit": imageFit,
        "imageHeight": imageHeight,
        "imageWidth": imageWidth,
        "maxImageHeight": maxImageHeight,
        "maxImageWidth": maxImageWidth,
        "minImageHeight": minImageHeight,
        "minImageWidth": minImageWidth,
        "multiSelect": multiSelect,
        "showLabel": showLabel,
    }
    if not isinstance(title, list):
        title = [title]
    title = flatten(title)
    choices = flatten(choices)
    if len(title) != 1:
        return [
            QuestionImagePickerModel(
                name=f"{name}_{i+1}",
                title=t,
                choices=choices,
                **args,
                **kwargs,
            )
            for i, t in enumerate(title)
        ]
    return QuestionImagePickerModel(
        name=name, title=title[0], choices=choices, **args, **kwargs
    )


def consent(
    title: str = "Do you consent to take part in the study?",
    error: str = "You can't continue without a consent",
    mode: str = "forbid",
    name: str = "consent",
    **kwargs,
) -> QuestionBooleanModel:
    """Create a question with a consent to take part in the study

    Args:
        title (str): The visible title of the question. Defaults to "Do you consent to take part in the study?".
        error (str): Error shown if a person doesn't consent.
        mode (str): What to do if a person doesn't consent. Can be 'forbid' (default, doesn't allow to continue) or 'end' (redirects to the end).
            For 'end' to work, set `triggers` in the `survey()` call to `[{"type": "complete", "expression": "{consent} = false"}]`. You can also
            set `completedHtmlOnCondition` in the `survey()` call to `[{"expression": "{consent} = false", "html": "You can't continue without a consent"}]`
            to show a custom message in that case.
        name (str): The label of the question. Defaults to "consent".
        kwargs: Other arguments passed to `yesno()`.
    """
    if mode == "forbid":
        return yesno(
            name,
            title,
            validators=expressionValidator(
                expression=f"{{{name}}} = true", error=error
            ),
            isRequired=True,
            **kwargs,
        )
    elif mode == "end":
        return yesno(
            name,
            title,
            isRequired=True,
            **kwargs,
        )
    else:
        raise ValueError(f"Unknown mode: {mode}")


def surveyFromJson(
    jsonPath: Path | str,
    folderName: Path | str = "survey",
    path: Path | str = os.getcwd(),
) -> None:
    """Create a survey from a JSON file

    Args:
        jsonPath (Path | str): Full path to the JSON file created with the creator (<https://surveyjs.io/free-survey-tool>).
        folderName (Path | str): The name of the folder where the survey will be created. Defaults to "survey".
        path (Path | str): The path where the survey will be created. Defaults to the current working directory.
    """
    if isinstance(jsonPath, str):
        jsonPath = Path(jsonPath)
    if isinstance(folderName, str):
        folderName = Path(folderName)
    if isinstance(path, str):
        path = Path(path)

    tempSurvey = SurveyModel(
        pages=[
            PageModel(
                name="temp", questions=[QuestionModel(name="temp", type="radiogroup")]
            )
        ]
    )

    tempSurvey.build(path=path, folderName=folderName, pauseBuild=True)

    with open(jsonPath, "r", encoding="UTF-8") as file:
        jsonFile = loads(file.read())  # use json.loads() to ensure proper structure

    with open(path / folderName / "src/survey.js", "w", encoding="UTF-8") as file:
        file.write(f"export const json = {dumps(jsonFile)}")

    subprocess.run("bun run build", cwd=path / folderName, shell=True, check=False)
