# app/schemas/__init__.py

# 从 user.py 文件中导入所有与用户和认证相关的 Schemas
from .user import (
    User,
    UserCreate,
    Token,
    TokenData,
    UserUpdate,
)

# 从 assessment.py 文件中导入所有与考核、题目、结果等相关的 Schemas
from .assessment import (
    Option,
    OptionCreate,
    Question,
    QuestionCreate,
    QuestionForExaminee,
    OptionForExaminee,
    AssessmentStart,
    SubmitAnswer,
    AnswerResponse,
    AssessmentBase,
    AssessmentCreate,
    AssessmentUpdate,
    Assessment
)

# 注意：base.py 中的 BaseSchema 通常不需要在这里导出，
# 因为其他的 Schema 并不直接从 app.schemas 导入它，
# 而是直接在各自的文件里 from pydantic import BaseModel。
# 所以我们暂时不需要处理 base.py。

from .platform import (
    Platform,
    PlatformCreate,
    PlatformUpdate
)

from .question_bank import (
    QuestionBank,
    QuestionBankCreate,
    QuestionBankUpdate
)

from .question import (
    Question,
    QuestionCreate,
    QuestionUpdate,
    Option,
    OptionCreate
)

from .procedure import (
    Procedure,
    ProcedureCreate,
    ProcedureUpdate
)


from .examinee import (
    AssessmentStartRequest,      # <--- 补上这个
    SubmitAnswerRequest,         # <--- 补上这个
    SubmitAnswerResponse,        # <--- 补上这个
    BlueprintOption,
    BlueprintQuestion,
    BlueprintProcedure,
    AssessmentBlueprintResponse,
    FinishAssessmentRequest
)

from .result import (
    AssessmentResultDetail
)



