# components/analytics_panel.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.data import get_analytics_data


def render_analytics_page(account: str):
    st.header(f"📊 Аналитика: {account}")
    
    # Добавляем стиль для лучшей презентации
    st.markdown("""
        <style>
        .main-container {
            padding: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Инициализация состояния
    if "target_revenue" not in st.session_state:
        st.session_state.target_revenue = 10000
    if "target_subs" not in st.session_state:
        st.session_state.target_subs = 80

    # Загрузка данных
    try:
        data = get_analytics_data(account)
        if data.empty:
            st.warning("⚠️ Нет данных для отображения аналитики")
            return
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {str(e)}")
        return

    # Расчет метрик
    total_rev = int(data["revenue"].sum()) if "revenue" in data.columns else 0
    total_subs = int(data["subs"].iloc[-1]) if "subs" in data.columns and len(data) > 0 else 0
    avg_watch = float(data["avg_watch"].mean()) if "avg_watch" in data.columns else 0.0

    # Расчет изменений
    if len(data) >= 2:
        prev_rev = int(data["revenue"].iloc[-2]) if "revenue" in data.columns else 0
        prev_subs = int(data["subs"].iloc[-2]) if "subs" in data.columns else 0
        rev_delta = total_rev - prev_rev
        subs_delta = total_subs - prev_subs
    else:
        rev_delta = 0
        subs_delta = 0

    # Стили
    st.markdown("""
        <style>
        .metric-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            min-height: 120px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 8px 0;
        }
        .metric-label {
            font-size: 13px;
            color: #aaa;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-delta-positive {
            color: #4CAF50;
            font-size: 14px;
            font-weight: 600;
        }
        .metric-delta-negative {
            color: #f44336;
            font-size: 14px;
            font-weight: 600;
        }
        .progress-card {
            background: rgba(255, 255, 255, 0.03);
            padding: 16px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin-bottom: 16px;
        }
        .achievement-card {
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 193, 7, 0.1) 100%);
            padding: 12px 16px;
            border-radius: 8px;
            border-left: 4px solid #FFD700;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .top-fan-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s;
        }
        .top-fan-card:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateX(4px);
        }
        .rank-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-weight: 700;
            font-size: 14px;
        }
        .rank-1 { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: #000; }
        .rank-2 { background: linear-gradient(135deg, #C0C0C0 0%, #808080 100%); color: #000; }
        .rank-3 { background: linear-gradient(135deg, #CD7F32 0%, #8B4513 100%); color: #fff; }
        </style>
    """, unsafe_allow_html=True)

    # ===== МЕТРИКИ =====
    col_top1, col_top2, col_top3 = st.columns(3)

    with col_top1:
        _render_metric_card(
            icon="💰",
            label="Доход за период",
            value=f"${total_rev:,}",
            delta=rev_delta,
            delta_suffix="$"
        )

    with col_top2:
        _render_metric_card(
            icon="👥",
            label="Подписчики",
            value=f"{total_subs:,}",
            delta=subs_delta,
            delta_suffix=""
        )

    with col_top3:
        _render_metric_card(
            icon="⏱️",
            label="Среднее время на стриме",
            value=f"{avg_watch:.1f} мин",
            delta=None,
            delta_suffix=""
        )

    st.markdown("---")

    # ===== ГРАФИКИ =====
    tab1, tab2, tab3 = st.tabs(["📈 Доход и подписчики", "⏰ Время на стриме", "📊 Сравнение"])

    with tab1:
        fig = _create_revenue_subs_chart(data)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig2 = _create_watch_time_chart(data)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig3 = _create_revenue_pie_chart(data)
            st.plotly_chart(fig3, use_container_width=True)
        with col_g2:
            fig4 = _create_growth_indicator(total_rev, total_subs)
            st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # ===== ГЕЙМИФИКАЦИЯ =====
    st.markdown("### 🎯 Цели и прогресс")

    col_plan1, col_plan2 = st.columns(2)

    with col_plan1:
        target_rev = st.number_input(
            "🎯 Цель по доходу на неделю, $",
            min_value=0,
            value=st.session_state.target_revenue,
            step=1000,
            key="target_revenue_input"
        )
        st.session_state.target_revenue = target_rev

        progress_rev = min(total_rev / target_rev, 1.0) if target_rev > 0 else 0
        remaining_rev = max(target_rev - total_rev, 0)

        st.markdown(f"""
            <div class="progress-card">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #aaa; font-size: 13px;">Прогресс</span>
                    <span style="font-weight: 600; color: #667eea;">{progress_rev*100:.1f}%</span>
                </div>
                <div style="margin-bottom: 12px;">
        """, unsafe_allow_html=True)
        
        st.progress(progress_rev)
        
        st.markdown(f"""
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12px;">
                    <span style="color: #4CAF50;">Достигнуто: ${total_rev:,}</span>
                    <span style="color: #ff9800;">Осталось: ${remaining_rev:,}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_plan2:
        target_subs = st.number_input(
            "🎯 Цель по подписчикам на неделю",
            min_value=0,
            value=st.session_state.target_subs,
            step=10,
            key="target_subs_input"
        )
        st.session_state.target_subs = target_subs

        progress_subs = min(total_subs / target_subs, 1.0) if target_subs > 0 else 0
        remaining_subs = max(target_subs - total_subs, 0)

        st.markdown(f"""
            <div class="progress-card">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #aaa; font-size: 13px;">Прогресс</span>
                    <span style="font-weight: 600; color: #667eea;">{progress_subs*100:.1f}%</span>
                </div>
                <div style="margin-bottom: 12px;">
        """, unsafe_allow_html=True)
        
        st.progress(progress_subs)
        
        st.markdown(f"""
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12px;">
                    <span style="color: #4CAF50;">Достигнуто: {total_subs:,}</span>
                    <span style="color: #ff9800;">Осталось: {remaining_subs:,}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ===== ТОПЫ И ДОСТИЖЕНИЯ =====
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("### 🏆 ТОП-3 Фанов по донатам")
        
        top_fans = [
            {"rank": 1, "name": "Mike", "badge": "🔥", "amount": 450},
            {"rank": 2, "name": "Dave", "badge": "", "amount": 300},
            {"rank": 3, "name": "Alex", "badge": "💎", "amount": 180},
        ]
        
        for fan in top_fans:
            st.markdown(f"""
                <div class="top-fan-card">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div class="rank-badge rank-{fan['rank']}">{fan['rank']}</div>
                        <div>
                            <div style="font-weight: 600; font-size: 15px;">
                                {fan['name']} {fan['badge']}
                            </div>
                        </div>
                    </div>
                    <div style="font-weight: 700; color: #4CAF50; font-size: 16px;">
                        ${fan['amount']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col_t2:
        st.markdown("### 🏅 Достижения недели")
        
        achievements = [
            {"icon": "✅", "text": "Закрыт план по доходу 3/5 дней", "color": "#4CAF50"},
            {"icon": "✅", "text": "2 стрима подряд с avg watch > 20 мин", "color": "#4CAF50"},
            {"icon": "🎯", "text": "Новый рекорд по подписчикам за день: +15", "color": "#FFD700"},
        ]
        
        if progress_rev >= 1.0:
            achievements.insert(0, {"icon": "🎉", "text": "Недельная цель по доходу выполнена!", "color": "#FF9800"})
        
        if progress_subs >= 1.0:
            achievements.insert(0, {"icon": "🎉", "text": "Недельная цель по подписчикам выполнена!", "color": "#FF9800"})
        
        for achievement in achievements:
            st.markdown(f"""
                <div class="achievement-card" style="border-left-color: {achievement['color']};">
                    <div style="font-size: 24px;">{achievement['icon']}</div>
                    <div style="flex: 1; font-size: 14px; font-weight: 500;">
                        {achievement['text']}
                    </div>
                </div>
            """, unsafe_allow_html=True)


def _render_metric_card(icon: str, label: str, value: str, delta, delta_suffix: str):
    """Отрисовка карточки метрики"""
    delta_html = ""
    if delta is not None:
        delta_class = "metric-delta-positive" if delta >= 0 else "metric-delta-negative"
        delta_icon = "↑" if delta >= 0 else "↓"
        delta_html = f'<div class="{delta_class}">{delta_icon} {abs(delta):,}{delta_suffix}</div>'
    
    st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


def _create_revenue_subs_chart(data):
    """Создание графика дохода и подписчиков"""
    fig = go.Figure()
    
    # Доход
    fig.add_trace(go.Scatter(
        x=data["day"],
        y=data["revenue"],
        name="Доход ($)",
        line=dict(color="#4CAF50", width=3),
        fill='tozeroy',
        fillcolor='rgba(76, 175, 80, 0.1)'
    ))
    
    # Подписчики
    fig.add_trace(go.Scatter(
        x=data["day"],
        y=data["subs"],
        name="Подписчики",
        line=dict(color="#667eea", width=3),
        yaxis="y2"
    ))
    
    fig.update_layout(
        title="Динамика дохода и подписчиков",
        xaxis=dict(title="День", showgrid=False),
        yaxis=dict(title="Доход ($)", showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis2=dict(title="Подписчики", overlaying="y", side="right", showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def _create_watch_time_chart(data):
    """Создание графика времени просмотра"""
    fig = px.bar(
        data,
        x="day",
        y="avg_watch",
        title="Среднее время зрителя на стриме (мин)",
        color="avg_watch",
        color_continuous_scale=["#667eea", "#764ba2"],
    )
    
    fig.update_layout(
        xaxis=dict(title="День", showgrid=False),
        yaxis=dict(title="Минуты", showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    
    return fig


def _create_revenue_pie_chart(data):
    """Создание круговой диаграммы распределения дохода"""
    if len(data) == 0:
        return go.Figure()
    
    # Группировка по периодам (первая/вторая половина)
    mid_point = len(data) // 2
    first_half = data.iloc[:mid_point]["revenue"].sum()
    second_half = data.iloc[mid_point:]["revenue"].sum()
    
    fig = go.Figure(data=[go.Pie(
        labels=["Первая половина", "Вторая половина"],
        values=[first_half, second_half],
        hole=0.4,
        marker=dict(colors=["#667eea", "#4CAF50"])
    )])
    
    fig.update_layout(
        title="Распределение дохода по периодам",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True
    )
    
    return fig


def _create_growth_indicator(revenue: int, subs: int):
    """Создание индикаторов роста"""
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=revenue,
        title={"text": "Общий доход ($)"},
        delta={'reference': revenue * 0.8, 'relative': False},
        domain={'x': [0, 0.5], 'y': [0.5, 1]}
    ))
    
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=subs,
        title={"text": "Подписчики"},
        delta={'reference': subs * 0.9, 'relative': False},
        domain={'x': [0.5, 1], 'y': [0.5, 1]}
    ))
    
    fig.update_layout(
        title="Индикаторы роста",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=300
    )
    
    return fig