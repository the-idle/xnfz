# # app/db/base.py
# # 这个文件用于让 Alembic (数据库迁移工具) 能够自动发现我们的模型

# from app.db.session import Base
# # 仅导入模型模块以注册所有模型到 Base.metadata（避免直接导入类名引发 ImportError）
# from app.models import user as user_models
# from app.models import assessment as assessment_models


# app/db/base.py
# 这个文件用于让 Alembic (数据库迁移工具) 能够自动发现我们的模型

from app.db.session import Base
# 仅导入模型模块以注册所有模型到 Base.metadata
# 这样做可以避免直接导入类名而引发的循环导入错误
from app.models import user_management
from app.models import question_management
from app.models import assessment_management