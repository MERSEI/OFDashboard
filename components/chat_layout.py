# components/chat_layout.py
import streamlit as st
from core.data import get_fans_df, get_chat_history
from core.ai import ai_warmup_suggestion
import time



def render_chats_page(account: str) -> None:
    st.header(f"💬 Чаты: {account}")

    # Инициализация выбранного фана
    if "selected_fan_id" not in st.session_state:
        fans_temp = get_fans_df(account)
        if not fans_temp.empty:
            st.session_state["selected_fan_id"] = fans_temp.iloc[0]["id"]
        else:
            st.session_state["selected_fan_id"] = None

    fans = get_fans_df(account)
    
    if fans.empty:
        st.warning("Нет доступных фанов")
        return

    col_list, col_chat, col_reply = st.columns([1.2, 2.2, 1.6])

    # ===== ЛЕВАЯ КОЛОНКА: СПИСОК ФАНОВ =====
    with col_list:
        st.markdown("### 👥 Фаны")
        
        segment_filter = st.multiselect(
            "Фильтр по сегментам",
            ["VIP", "Buyer", "Free"],
            default=[],
            key="segment_filter"
        )
        
        # Если фильтр пустой - показываем всех
        if segment_filter:
            filtered = fans[fans["segment"].isin(segment_filter)]
        else:
            filtered = fans
        
        if filtered.empty:
            st.info("Нет фанов с выбранными сегментами")
        else:
            # Проверка валидности выбранного фана
            if st.session_state["selected_fan_id"] not in filtered["id"].values:
                st.session_state["selected_fan_id"] = filtered.iloc[0]["id"]
            
            _render_fans_list(filtered)

    # Получаем текущего фана
    if st.session_state["selected_fan_id"] is None:
        st.warning("Выберите фана из списка")
        return
        
    current_fan_df = fans[fans["id"] == st.session_state["selected_fan_id"]]
    if current_fan_df.empty:
        st.error("Выбранный фан не найден")
        return
        
    current_fan = current_fan_df.iloc[0]
    history = get_chat_history(current_fan["id"])

    # ===== ЦЕНТР: ЧАТ =====
    with col_chat:
        st.markdown(f"### 💬 Чат с **{current_fan['name']}**")
        _render_chat_history(history)

    # ===== ПРАВАЯ КОЛОНКА: ОТВЕТ + AI =====
    with col_reply:
        st.markdown("### ✍️ Ответ")
        
        if st.button("✨ AI-подсказка для разогрева", use_container_width=True, type="secondary"):
            with st.spinner("Генерирую подсказку..."):
                suggestion = ai_warmup_suggestion(history, current_fan["name"])
                st.session_state["ai_suggestion"] = suggestion
                st.rerun()

        default_text = st.session_state.get("ai_suggestion", "")
        reply_text = st.text_area(
            "Сообщение",
            value=default_text,
            height=160,
            placeholder="Напишите ваше сообщение...",
            key="reply_text"
        )

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button(
                "📤 Отправить",
                use_container_width=True,
                type="primary",
                disabled=not reply_text.strip(),
            ):
                # МОК: эмулируем отправку
                with st.spinner("Отправляю…"):
                    time.sleep(0.8)  # вернёт красивый эффект, апп работает как мок

                st.success("✅ Сообщение отправлено")

                # Чистим только ai_suggestion, сам текст очистится после rerun
                if "ai_suggestion" in st.session_state:
                    st.session_state["ai_suggestion"] = ""

                # ВАЖНО: не трогаем st.session_state["reply_text"] тут
                st.rerun()
        
        with col_r2:
            if st.button(
                "🗑️ Очистить",
                use_container_width=True,
                type="secondary",
                disabled=not reply_text.strip(),
            ):
                st.session_state["reply_text"] = ""
                st.session_state["ai_suggestion"] = ""
                st.rerun()



        st.markdown("---")
        
        # Информационная карточка фана
        _render_fan_info_card(current_fan)


def _render_fans_list(filtered_fans) -> None:
    """Отрисовка списка фанов с улучшенным дизайном"""
    st.markdown("""
        <style>
        .fan-card {
            padding: 12px;
            margin: 6px 0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
            border: 2px solid transparent;
        }
        .fan-card:hover {
            transform: translateX(4px);
            background-color: rgba(255, 255, 255, 0.05);
        }
        .fan-card-selected {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: 2px solid #764ba2;
            box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
        }
        .fan-card-vip {
            border-left: 4px solid #FFD700;
        }
        .fan-card-buyer {
            border-left: 4px solid #4CAF50;
        }
        .fan-card-free {
            border-left: 4px solid #9E9E9E;
        }
        .fan-name {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
        }
        .fan-revenue {
            font-size: 12px;
            color: #4CAF50;
            font-weight: 500;
        }
        .fan-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            margin-right: 6px;
        }
        .badge-vip { background: #FFD700; color: #000; }
        .badge-buyer { background: #4CAF50; color: #fff; }
        .badge-free { background: #9E9E9E; color: #fff; }
        </style>
    """, unsafe_allow_html=True)
    
    for _, row in filtered_fans.iterrows():
        is_selected = row["id"] == st.session_state["selected_fan_id"]
        
        # Иконки и стили
        segment_icon = {"VIP": "💎", "Buyer": "💰", "Free": "👤"}
        badge_class = {"VIP": "badge-vip", "Buyer": "badge-buyer", "Free": "badge-free"}
        card_class = {"VIP": "fan-card-vip", "Buyer": "fan-card-buyer", "Free": "fan-card-free"}
        segment = row["segment"]
        
        new_indicator = "🔴 " if row["has_new"] else ""
        
        # Кнопка для каждого фана с применением стилей
        button_label = f"{segment_icon[segment]} {new_indicator}{row['name']} · ${row['revenue']}"
        
        # Применяем стили карточки через markdown
        st.markdown(f"""
            <div class="{card_class[segment]}" style="
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                padding: 12px;
                border-radius: 10px;
                margin: 6px 0;
                border: 2px solid {'#764ba2' if is_selected else 'transparent'};
                {'box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);' if is_selected else ''}
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 600;">
                        {button_label}
                    </div>
                    <div class="{badge_class[segment]} fan-badge" style="background: {{'#FFD700' if segment == 'VIP' else '#4CAF50' if segment == 'Buyer' else '#9E9E9E'}}; color: {'#000' if segment == 'VIP' else '#fff'}">
                        {segment}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(
            "Выбрать",
            key=f"fan_{row['id']}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            st.session_state["selected_fan_id"] = row["id"]
            st.rerun()


def _render_fan_info_card(fan) -> None:
    """Информационная карточка выбранного фана"""
    segment_colors = {
        "VIP": "#FFD700",
        "Buyer": "#4CAF50",
        "Free": "#9E9E9E"
    }
    
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            padding: 16px;
            border-radius: 12px;
            border-left: 4px solid {segment_colors[fan['segment']]};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 13px; color: #aaa;">Сегмент</span>
                <span style="font-weight: 600; color: {segment_colors[fan['segment']]};">{fan['segment']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px; color: #aaa;">Общий доход</span>
                <span style="font-weight: 700; color: #4CAF50; font-size: 16px;">${fan['revenue']}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def _render_chat_history(history) -> None:
    """Отрисовка истории чата с улучшенным дизайном"""
    st.markdown("""
        <style>
        .chat-history {
            max-height: 550px;
            overflow-y: auto;
            padding: 16px;
            border-radius: 12px;
            background: linear-gradient(180deg, rgba(17, 17, 17, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        .chat-history::-webkit-scrollbar {
            width: 6px;
        }
        .chat-history::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }
        .chat-history::-webkit-scrollbar-thumb {
            background: rgba(102, 126, 234, 0.5);
            border-radius: 10px;
        }
        .chat-history::-webkit-scrollbar-thumb:hover {
            background: rgba(102, 126, 234, 0.7);
        }
        .msg-user {
            text-align: right;
            margin-bottom: 12px;
            animation: slideInRight 0.3s ease;
        }
        .msg-bubble-user {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 10px 14px;
            border-radius: 18px 18px 4px 18px;
            font-size: 14px;
            max-width: 75%;
            word-wrap: break-word;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        .msg-assistant {
            text-align: left;
            margin-bottom: 12px;
            animation: slideInLeft 0.3s ease;
        }
        .msg-bubble-assistant {
            display: inline-block;
            background: rgba(66, 66, 66, 0.8);
            color: #fff;
            padding: 10px 14px;
            border-radius: 18px 18px 18px 4px;
            font-size: 14px;
            max-width: 75%;
            word-wrap: break-word;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        .msg-time {
            font-size: 10px;
            color: #888;
            margin-top: 4px;
            font-style: italic;
        }
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="chat-history">', unsafe_allow_html=True)

    if not history:
        st.markdown(
            '<div style="text-align: center; color: #666; padding: 40px;">Нет сообщений</div>',
            unsafe_allow_html=True
        )
    else:
        for msg in history:
            if msg["role"] == "user":
                st.markdown(f"""
                    <div class="msg-user">
                        <div class="msg-bubble-user">{msg['text']}</div>
                        <div class="msg-time">{msg['time']}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="msg-assistant">
                        <div class="msg-bubble-assistant">{msg['text']}</div>
                        <div class="msg-time">{msg['time']}</div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)