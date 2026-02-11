# components/content_panel.py
import streamlit as st
from core.ai import (
    fake_generate_images,
    fake_generate_videos,
    estimate_generation_cost,
)


def render_content_page(account: str):
    st.set_page_config(layout="wide", page_title="Content Generator")
    st.header(f"🎥 Контент: {account}")
    
    # Добавляем стиль для лучшей презентации
    st.markdown("""
        <style>
        .main-container {
            padding: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Инициализация состояния
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = None
    if "selected_variants" not in st.session_state:
        st.session_state.selected_variants = []

    col_left, col_right = st.columns([1.5, 1.8])

    # ===== ЛЕВАЯ ЧАСТЬ: НАСТРОЙКИ ГЕНЕРАЦИИ =====
    with col_left:
        st.markdown("### ⚙️ Настройки генерации")
        
        with st.container():
            st.markdown("""
                <style>
                .settings-section {
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
                    padding: 20px;
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    margin-bottom: 16px;
                }
                .cost-card {
                    background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(67, 160, 71, 0.1) 100%);
                    padding: 16px;
                    border-radius: 10px;
                    border-left: 4px solid #4CAF50;
                    margin: 12px 0;
                }
                .price-display {
                    font-size: 24px;
                    font-weight: 700;
                    color: #4CAF50;
                    text-align: center;
                    margin: 8px 0;
                }
                .section-divider {
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    margin: 20px 0;
                }
                </style>
            """, unsafe_allow_html=True)

            # Модель
            model_name = st.selectbox(
                "🎨 Модель",
                ["Base_SDXL", "Sexy_v3", "AnimePink"],
                help="Выберите базовую модель для генерации"
            )

            # LoRA настройки
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            lora_mode = st.radio(
                "🔧 LoRA",
                ["Без LoRA", "ID LoRA", "Файл LoRA"],
                horizontal=True
            )

            lora_id = ""
            lora_file = None
            if lora_mode == "ID LoRA":
                lora_id = st.text_input(
                    "LoRA ID",
                    placeholder="sexy_lora_v2",
                    help="Введите ID или имя LoRA модели"
                )
            elif lora_mode == "Файл LoRA":
                lora_file = st.file_uploader(
                    "Загрузить LoRA-файл",
                    type=["safetensors"],
                    help="Загрузите свой файл LoRA (.safetensors)"
                )
                if lora_file:
                    st.success(f"✅ Загружен: {lora_file.name}")

            # Тип контента
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            col_type, col_cat = st.columns(2)
            with col_type:
                content_type = st.selectbox(
                    "📁 Тип",
                    ["Фото", "Видео"]
                )
            with col_cat:
                subcategory = st.selectbox(
                    "🏷️ Категория",
                    ["NSFW", "Бикини", "Soft"]
                )

            # Промпт
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            prompt = st.text_area(
                "✍️ Промпт",
                placeholder="Пример: девушка в красном бикини, пляж, закат, улыбка, высокое качество, 4k",
                height=100,
                help="Опишите желаемое изображение/видео"
            )

            # Количество вариантов
            n_variants = st.slider(
                "🔢 Количество вариантов",
                min_value=1,
                max_value=8,
                value=4,
                help="Сколько вариантов сгенерировать за раз"
            )

        # Калькулятор стоимости
        st.markdown("### 💰 Калькулятор стоимости")
        
        with st.expander("⚙️ Настройки расчета", expanded=False):
            est_tokens = st.slider(
                "Оценка токенов",
                min_value=500,
                max_value=8000,
                value=2000,
                step=500,
                help="1k токенов ≈ 1 изображение"
            )
            price_per_1k = st.number_input(
                "Цена за 1k токенов, $",
                min_value=0.0,
                max_value=1.0,
                value=0.002,
                step=0.001,
                format="%.4f"
            )
        
        # Расчет стоимости
        cost = estimate_generation_cost(est_tokens, price_per_1k)
        markup = st.slider(
            "📈 Наценка (x)",
            min_value=1.0,
            max_value=10.0,
            value=3.0,
            step=0.5
        )
        sell_price = cost * markup
        
        st.markdown(f"""
            <div class="cost-card">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span style="color: #aaa; font-size: 13px;">Себестоимость:</span>
                    <span style="color: #fff; font-weight: 600;">${cost:.4f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span style="color: #aaa; font-size: 13px;">Наценка:</span>
                    <span style="color: #fff; font-weight: 600;">{markup}x</span>
                </div>
                <div style="border-top: 1px solid rgba(255, 255, 255, 0.2); padding-top: 12px;">
                    <div style="color: #aaa; font-size: 13px; text-align: center; margin-bottom: 4px;">
                        Рекомендуемая цена продажи
                    </div>
                    <div class="price-display">${sell_price:.2f}</div>
                    <div style="color: #4CAF50; font-size: 12px; text-align: center;">
                        Прибыль: ${(sell_price - cost):.2f} ({((markup - 1) * 100):.0f}%)
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Кнопка генерации
        st.markdown("---")
        generate_disabled = not prompt.strip()
        
        if st.button(
            "🚀 Сгенерировать контент",
            use_container_width=True,
            type="primary",
            disabled=generate_disabled,
            help="Введите промпт для генерации" if generate_disabled else "Запустить генерацию"
        ):
            with st.spinner("🎨 Генерирую контент..."):
                params = {
                    "prompt": prompt,
                    "model_name": model_name,
                    "lora_id": lora_id,
                    "content_type": content_type,
                    "subcategory": subcategory,
                    "n_variants": n_variants,
                }
                
                if content_type == "Фото":
                    urls = fake_generate_images(
                        prompt=params["prompt"],
                        model_name=params["model_name"],
                        lora_id=params["lora_id"],
                        n=params["n_variants"],
                    )
                    st.session_state.generated_content = {
                        "type": "image",
                        "urls": urls,
                        "params": params
                    }
                else:
                    urls = fake_generate_videos(
                        prompt=params["prompt"],
                        model_name=params["model_name"],
                        lora_id=params["lora_id"],
                        n=params["n_variants"],
                    )
                    st.session_state.generated_content = {
                        "type": "video",
                        "urls": urls,
                        "params": params
                    }
                
                st.session_state.selected_variants = []
                st.rerun()

    # ===== ПРАВАЯ ЧАСТЬ: РЕЗУЛЬТАТЫ И ВЫБОР =====
    with col_right:
        st.markdown("### 🖼️ Результаты генерации")
        
        if st.session_state.generated_content:
            content = st.session_state.generated_content
            
            # Заголовок с информацией
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                    padding: 12px 16px;
                    border-radius: 8px;
                    margin-bottom: 16px;
                    border-left: 4px solid #667eea;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600;">
                            {'📸 Фотографии' if content['type'] == 'image' else '🎬 Видео'}
                        </span>
                        <span style="color: #4CAF50; font-weight: 600;">
                            {len(content['urls'])} вариантов
                        </span>
                    </div>
                    <div style="font-size: 12px; color: #aaa; margin-top: 4px;">
                        Модель: {content['params']['model_name']} • {content['params']['subcategory']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Отображение результатов
            if content["type"] == "image":
                _render_image_results(content["urls"])
            else:
                _render_video_results(content["urls"])
            
            # Действия с выбранным контентом
            st.markdown("---")
            selected_count = len(st.session_state.selected_variants)
            
            if selected_count > 0:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(67, 160, 71, 0.15) 100%);
                        padding: 12px;
                        border-radius: 8px;
                        text-align: center;
                        margin-bottom: 12px;
                    ">
                        <span style="font-size: 16px; font-weight: 600; color: #4CAF50;">
                            ✅ Выбрано: {selected_count} {_get_variant_word(selected_count)}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
                
                col_save, col_send = st.columns(2)
                with col_save:
                    if st.button("💾 Сохранить", use_container_width=True, type="secondary"):
                        st.success(f"✅ Сохранено {selected_count} {_get_variant_word(selected_count)}")
                with col_send:
                    if st.button("📤 Отправить фану", use_container_width=True, type="primary"):
                        st.success(f"✅ Отправлено {selected_count} {_get_variant_word(selected_count)}")
            
            # Кнопка перегенерации
            st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
            if st.button(
                "🔁 Перегенерировать с теми же настройками",
                use_container_width=True,
                type="secondary"
            ):
                with st.spinner("🎨 Перегенерирую..."):
                    params = content["params"]
                    
                    if params["content_type"] == "Фото":
                        urls = fake_generate_images(
                            prompt=params["prompt"],
                            model_name=params["model_name"],
                            lora_id=params["lora_id"],
                            n=params["n_variants"],
                        )
                        st.session_state.generated_content = {
                            "type": "image",
                            "urls": urls,
                            "params": params
                        }
                    else:
                        urls = fake_generate_videos(
                            prompt=params["prompt"],
                            model_name=params["model_name"],
                            lora_id=params["lora_id"],
                            n=params["n_variants"],
                        )
                        st.session_state.generated_content = {
                            "type": "video",
                            "urls": urls,
                            "params": params
                        }
                    
                    st.session_state.selected_variants = []
                    st.rerun()
            
            # Кнопка очистки
            if st.button("🗑️ Очистить результаты", use_container_width=True):
                st.session_state.generated_content = None
                st.session_state.selected_variants = []
                st.rerun()
        else:
            # Пустое состояние
            st.markdown("""
                <div style="
                    text-align: center;
                    padding: 60px 20px;
                    color: #666;
                    border: 2px dashed rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    margin-top: 20px;
                ">
                    <div style="font-size: 48px; margin-bottom: 16px;">🎨</div>
                    <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">
                        Нет сгенерированного контента
                    </div>
                    <div style="font-size: 13px; color: #888;">
                        Настройте параметры слева и нажмите "Сгенерировать"
                    </div>
                </div>
            """, unsafe_allow_html=True)


def _render_image_results(urls: list) -> None:
    """Отрисовка результатов генерации изображений"""
    st.markdown("""
        <style>
        .image-card {
            position: relative;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 16px;
            border: 2px solid transparent;
            transition: all 0.3s;
        }
        .image-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
            transform: scale(1.02);
        }
        .image-card-selected {
            border-color: #4CAF50 !important;
            box-shadow: 0 4px 20px rgba(76, 175, 80, 0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    for i, url in enumerate(urls):
        is_selected = i in st.session_state.selected_variants
        
        card_class = "image-card-selected" if is_selected else ""
        
        col_img, col_check = st.columns([4, 1])
        
        with col_img:
            st.markdown(f'<div class="image-card {card_class}">', unsafe_allow_html=True)
            st.image(url, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_check:
            st.markdown('<div style="padding-top: 40%;"></div>', unsafe_allow_html=True)
            if st.checkbox(
                "✓",
                value=is_selected,
                key=f"img_sel_{i}",
                label_visibility="collapsed"
            ):
                if i not in st.session_state.selected_variants:
                    st.session_state.selected_variants.append(i)
                    st.rerun()
            else:
                if i in st.session_state.selected_variants:
                    st.session_state.selected_variants.remove(i)
                    st.rerun()


def _render_video_results(urls: list) -> None:
    """Отрисовка результатов генерации видео"""
    for i, url in enumerate(urls):
        is_selected = i in st.session_state.selected_variants
        
        st.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                padding: 16px;
                border-radius: 10px;
                margin-bottom: 12px;
                border-left: 4px solid {'#4CAF50' if is_selected else '#667eea'};
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; margin-bottom: 4px;">🎬 Вариант {i + 1}</div>
                        <div style="font-size: 12px; color: #888; font-family: monospace;">{url}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.checkbox(
            f"✓ Выбрать вариант {i + 1}",
            value=is_selected,
            key=f"vid_sel_{i}"
        ):
            if i not in st.session_state.selected_variants:
                st.session_state.selected_variants.append(i)
                st.rerun()
        else:
            if i in st.session_state.selected_variants:
                st.session_state.selected_variants.remove(i)
                st.rerun()


def _get_variant_word(count: int) -> str:
    """Получить правильное склонение слова 'вариант'"""
    if count % 10 == 1 and count % 100 != 11:
        return "вариант"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return "варианта"
    else:
        return "вариантов"