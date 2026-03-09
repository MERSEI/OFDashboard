from __future__ import annotations
import streamlit as st
from datetime import datetime, timedelta
import hashlib
from components.chat_layout import render_chats_page
from components.analytics_panel import render_analytics_page
from components.content_panel import render_content_page

# Конфигурация страницы
st.set_page_config(
    page_title="OF Operator Hub",
    page_icon="💎",
    layout="wide"
)

# База данных пользователей (в продакшене заменить на настоящую БД)
USERS_DB = {
    "admin": {
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "plan": "premium",
        "expires": datetime.now() + timedelta(days=365),
        "accounts": ["AI_Girl_1", "AI_Girl_2", "AI_Girl_3"],
        "features": ["chats", "content", "analytics", "ai_suggestions"]
    },
    "operator1": {
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "plan": "basic",
        "expires": datetime.now() + timedelta(days=30),
        "accounts": ["AI_Girl_1"],
        "features": ["chats", "content"]
    },
    "demo": {
        "password": hashlib.sha256("demo".encode()).hexdigest(),
        "plan": "trial",
        "expires": datetime.now() + timedelta(days=7),
        "accounts": ["AI_Girl_1"],
        "features": ["chats"]
    }
}

PLANS = {
    "trial": {"name": "Trial", "color": "#9E9E9E", "icon": "🆓"},
    "basic": {"name": "Basic", "color": "#4CAF50", "icon": "💚"},
    "premium": {"name": "Premium", "color": "#FFD700", "icon": "💎"}
}


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_credentials(username: str, password: str) -> dict | None:
    """Проверка учетных данных"""
    if username in USERS_DB:
        user = USERS_DB[username]
        if user["password"] == hash_password(password):
            # Проверка срока действия подписки
            if user["expires"] > datetime.now():
                return {
                    "username": username,
                    "plan": user["plan"],
                    "expires": user["expires"],
                    "accounts": user["accounts"],
                    "features": user["features"]
                }
    return None


def render_login_page():
    """Страница входа"""
    st.markdown("""
        <style>
        .login-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 40px;
        }
        .login-logo {
            font-size: 64px;
            margin-bottom: 16px;
        }
        .login-title {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        .login-subtitle {
            color: #aaa;
            font-size: 14px;
        }
        .login-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            padding: 32px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        .demo-credentials {
            background: rgba(255, 152, 0, 0.1);
            border: 1px solid rgba(255, 152, 0, 0.3);
            border-radius: 8px;
            padding: 12px;
            margin-top: 20px;
            font-size: 12px;
        }
        .demo-credentials-title {
            font-weight: 600;
            color: #ff9800;
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Заголовок
    st.markdown("""
        <div class="login-header">
            <div class="login-logo">💎</div>
            <div class="login-title">OF Operator Hub</div>
            <div class="login-subtitle">Единое пространство для операторов AI-моделей</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Форма входа
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "👤 Логин",
            placeholder="Введите ваш логин",
            key="login_username"
        )
        
        password = st.text_input(
            "🔒 Пароль",
            type="password",
            placeholder="Введите ваш пароль",
            key="login_password"
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            submit = st.form_submit_button(
                "🚀 Войти",
                use_container_width=True,
                type="primary"
            )
        with col2:
            st.form_submit_button(
                "Забыли пароль?",
                use_container_width=True,
                type="secondary",
                disabled=True
            )
        
        if submit:
            if not username or not password:
                st.error("❌ Пожалуйста, заполните все поля")
            else:
                user_data = verify_credentials(username, password)
                if user_data:
                    st.session_state["authenticated"] = True
                    st.session_state["user_data"] = user_data
                    st.success("✅ Вход выполнен успешно!")
                    st.rerun()
                else:
                    st.error("❌ Неверный логин или пароль, либо подписка истекла")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Демо-учетки
    st.markdown("""
        <div class="demo-credentials">
            <div class="demo-credentials-title">🎯 Демо-доступы для тестирования:</div>
            <div style="font-family: monospace; line-height: 1.8;">
                <strong>Premium:</strong> admin / admin123<br>
                <strong>Basic:</strong> operator1 / password123<br>
                <strong>Trial:</strong> demo / demo
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_subscription_info():
    """Информация о подписке в сайдбаре"""
    user_data = st.session_state.get("user_data", {})
    plan = user_data.get("plan", "trial")
    expires = user_data.get("expires", datetime.now())
    username = user_data.get("username", "Unknown")
    
    plan_info = PLANS.get(plan, PLANS["trial"])
    days_left = (expires - datetime.now()).days
    
    st.sidebar.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
            padding: 16px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
        ">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <div style="font-size: 32px;">{plan_info['icon']}</div>
                <div>
                    <div style="font-size: 16px; font-weight: 700; color: {plan_info['color']};">
                        {plan_info['name']} Plan
                    </div>
                    <div style="font-size: 12px; color: #aaa;">
                        👤 {username}
                    </div>
                </div>
            </div>
            <div style="
                background: rgba(0, 0, 0, 0.2);
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                text-align: center;
            ">
                ⏰ Осталось: <strong>{days_left} дней</strong>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_logout_button():
    """Кнопка выхода"""
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Выйти из аккаунта", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.rerun()


def check_feature_access(feature: str) -> bool:
    """Проверка доступа к функции"""
    user_data = st.session_state.get("user_data", {})
    features = user_data.get("features", [])
    return feature in features


def render_upgrade_notice(feature_name: str):
    """Уведомление об обновлении подписки"""
    st.warning(f"""
        ⚠️ **Функция "{feature_name}" недоступна на вашем тарифе**
        
        Обновите подписку до Basic или Premium для доступа к этой функции.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("💎 Обновить до Premium", use_container_width=True, type="primary")
    with col2:
        st.button("💚 Обновить до Basic", use_container_width=True, type="secondary")


def main():
    """Главная функция приложения"""
    # Инициализация состояния
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    # Проверка аутентификации
    if not st.session_state.get("authenticated", False):
        render_login_page()
        return
    
    # Проверка валидности сессии
    user_data = st.session_state.get("user_data", {})
    if user_data.get("expires", datetime.now()) <= datetime.now():
        st.error("⚠️ Срок действия вашей подписки истек")
        st.session_state.clear()
        st.rerun()
        return
    
    # Сайдбар для авторизованных пользователей
    st.sidebar.title("🚀 OF Operator Hub")
    st.sidebar.markdown("Единое пространство для операторов AI-моделей")
    
    # Информация о подписке
    render_subscription_info()
    
    # Выбор аккаунта
    available_accounts = user_data.get("accounts", [])
    account = st.session_state.get("current_account", "AI_Girl_1")
    if available_accounts:
        account = st.sidebar.selectbox(
            "🎭 Аккаунт модели",
            available_accounts,
            key="account_selector"
        )
        st.session_state["current_account"] = account
    else:
        st.sidebar.warning("⚠️ У вас нет доступных аккаунтов")
    
    st.sidebar.markdown("---")
    
    # Навигация
    st.sidebar.markdown("### 📱 Навигация")
    
    pages = {
        "💬 Чаты": ("chats", "chats_page"),
        "🎥 Контент": ("content", "content_page"),
        "📊 Аналитика": ("analytics", "analytics_page"),
    }
    
    for page_name, (feature, page_key) in pages.items():
        has_access = check_feature_access(feature)
        
        if has_access:
            if st.sidebar.button(
                page_name,
                use_container_width=True,
                type="primary" if st.session_state.get("current_page") == page_key else "secondary"
            ):
                st.session_state["current_page"] = page_key
                st.rerun()
        else:
            st.sidebar.button(
                f"{page_name} 🔒",
                use_container_width=True,
                disabled=True,
                help=f"Недоступно на вашем тарифе"
            )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("v0.2 · Subscription MVP")

    # Кнопка выхода
    render_logout_button()
    
    # Отображение контента страницы
    current_page = st.session_state.get("current_page", "chats_page")
    
    if current_page == "chats_page":
        if check_feature_access("chats"):
            account = st.session_state.get("current_account", "AI_Girl_1")
            render_chats_page(account)
        else:
            render_upgrade_notice("Чаты")

    
    elif current_page == "content_page":
        if check_feature_access("content"):
            render_content_page(account)
        else:
            render_upgrade_notice("Генерация контента")

    elif current_page == "analytics_page":
        if check_feature_access("analytics"):
            render_analytics_page(account)
        else:
            render_upgrade_notice("Аналитика")


if __name__ == "__main__":
    main()