import random
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Тренажер кода Хэмминга (7,4)", layout="wide")

# --- Алгоритмы теории информации (Хэмминг 7,4) ---


def text_to_nibbles(text: str):
    """Преобразует строку в список 4-битных блоков (полубайтов)."""
    raw_bytes = text.encode("utf-8")
    nibbles = []
    for b in raw_bytes:
        nibbles.append((b >> 4) & 0x0F)  # Старшие 4 бита
        nibbles.append(b & 0x0F)  # Младшие 4 бита
    return nibbles


def nibbles_to_text(nibbles):
    """Собирает список 4-битных блоков обратно в UTF-8 строку."""
    byte_vals = []
    for i in range(0, len(nibbles), 2):
        if i + 1 < len(nibbles):
            b = (nibbles[i] << 4) | nibbles[i + 1]
            byte_vals.append(b)
    return bytes(byte_vals).decode("utf-8", errors="replace")


def encode_hamming74(d_int: int):
    """Кодирует 4 бита данных в 7-битный кодовый вектор."""
    d = [(d_int >> (3 - i)) & 1 for i in range(4)]
    d1, d2, d3, d4 = d[0], d[1], d[2], d[3]
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4
    return [p1, p2, d1, p3, d2, d3, d4]


def decode_hamming74(r_bits):
    """Вычисляет синдром, исправляет одиночную ошибку и извлекает 4 бита данных."""
    r = list(r_bits)
    s1 = r[0] ^ r[2] ^ r[4] ^ r[6]
    s2 = r[1] ^ r[2] ^ r[5] ^ r[6]
    s3 = r[3] ^ r[4] ^ r[5] ^ r[6]

    syndrome = (s3 << 2) | (s2 << 1) | s1
    corrected_pos = 0

    if syndrome != 0:
        corrected_pos = syndrome  # Номер бита с ошибкой (1-7)
        r[corrected_pos - 1] ^= 1  # Исправление бита

    # Извлечение информационных бит: позиции 3, 5, 6, 7
    data_bits = [r[2], r[4], r[5], r[6]]
    nibble_val = (
        (data_bits[0] << 3)
        | (data_bits[1] << 2)
        | (data_bits[2] << 1)
        | data_bits[3]
    )

    return syndrome, corrected_pos, r, nibble_val


# --- Интерфейс приложения ---

st.title("🛰️ Облачный симулятор передачи данных и кода Хэмминга (7,4)")
st.caption(
    "Модель зашумленного канала связи, обнаружения и исправления ошибок в реальном времени"
)

# Ввод исходных данных
user_text = st.text_input(
    "1. Введите исходное сообщение для отправки в канал:",
    value="СВЯЗЬ",
    max_chars=20,
    help="Рекомендуется от 1 до 10 символов для наглядного отображения сетки битов",
)

if not user_text:
    st.warning("Введите хотя бы один символ для начала передачи.")
    st.stop()

# Кодирование сообщения
nibbles = text_to_nibbles(user_text)
total_blocks = len(nibbles)
clean_encoded_blocks = [encode_hamming74(n) for n in nibbles]
total_bits = total_blocks * 7

# Инициализация маски шума в session_state
if (
    "last_text" not in st.session_state
    or st.session_state.last_text != user_text
):
    st.session_state.last_text = user_text
    st.session_state.noise_mask = [0] * total_bits

st.divider()

# Управление искажениями
st.subheader("2. Канал связи и внесение помех")
col_noise1, col_noise2 = st.columns([2, 1])

with col_noise1:
    noise_pct = st.slider("Задать процент случайных искажений в канале:", 0, 50, 0)
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🎲 Наложить случайный шум", use_container_width=True):
            num_flips = int(total_bits * (noise_pct / 100))
            new_mask = [0] * total_bits
            if num_flips > 0:
                flip_indices = random.sample(
                    range(total_bits), min(num_flips, total_bits)
                )
                for idx in flip_indices:
                    new_mask[idx] = 1
            st.session_state.noise_mask = new_mask
            st.rerun()
    with col_btn2:
        if st.button("🔄 Очистить канал (убрать шум)", use_container_width=True):
            st.session_state.noise_mask = [0] * total_bits
            st.rerun()

with col_noise2:
    st.info(
        "💡 **Интерактив:** Вы также можете кликнуть по любому биту ниже, чтобы инвертировать его вручную."
    )

# Отображение битовой сетки для ручного клика
with st.expander(
    f"🛠️ Ручная сетка битов ({total_blocks} кодовых блоков по 7 бит)",
    expanded=True,
):
    st.write(
        "Нажмите на чекбокс под битом, чтобы **исказить (инвертировать)** его:"
    )

    bit_labels = ["p1 (1)", "p2 (2)", "d1 (3)", "p3 (4)", "d2 (5)", "d3 (6)", "d4 (7)"]

    for b_idx in range(total_blocks):
        st.markdown(
            f"**Блок {b_idx + 1}** (Полубайт #{b_idx + 1} сообщения):"
        )
        cols = st.columns(7)
        for bit_pos in range(7):
            global_bit_idx = b_idx * 7 + bit_pos
            orig_bit = clean_encoded_blocks[b_idx][bit_pos]
            is_flipped = bool(st.session_state.noise_mask[global_bit_idx])
            current_bit = orig_bit ^ (1 if is_flipped else 0)

            with cols[bit_pos]:
                bit_style = f"**:red[{current_bit}]**" if is_flipped else f"**:green[{current_bit}]**"
                st.caption(bit_labels[bit_pos])
                st.markdown(f"Значение: {bit_style}")
                if st.checkbox(
                    "Исказить",
                    value=is_flipped,
                    key=f"chk_{global_bit_idx}",
                    label_visibility="collapsed",
                ):
                    if not is_flipped:
                        st.session_state.noise_mask[global_bit_idx] = 1
                        st.rerun()
                else:
                    if is_flipped:
                        st.session_state.noise_mask[global_bit_idx] = 0
                        st.rerun()

st.divider()

# --- Декодирование и исправление на стороне приемника ---
received_blocks = []
corrected_blocks = []
restored_nibbles = []
raw_received_nibbles = []
report_data = []
total_errors_detected = 0

for b_idx in range(total_blocks):
    rec_block = []
    for bit_pos in range(7):
        global_bit_idx = b_idx * 7 + bit_pos
        bit_val = clean_encoded_blocks[b_idx][bit_pos] ^ st.session_state.noise_mask[global_bit_idx]
        rec_block.append(bit_val)
    received_blocks.append(rec_block)

    # Приемник без исправления ошибок
    raw_nibble = (
        (rec_block[2] << 3)
        | (rec_block[4] << 2)
        | (rec_block[5] << 1)
        | rec_block[6]
    )
    raw_received_nibbles.append(raw_nibble)

    # Декодирование с синдромным исправлением
    syn, err_pos, corr_block, valid_nibble = decode_hamming74(rec_block)
    corrected_blocks.append(corr_block)
    restored_nibbles.append(valid_nibble)

    if err_pos > 0:
        total_errors_detected += 1
        status = f"⚠️ Ошибка в бите #{err_pos} -> Исправлено"
    else:
        status = "✅ Без ошибок"

    report_data.append(
        {
            "Блок": f"#{b_idx + 1}",
            "Передано (7 бит)": "".join(map(str, clean_encoded_blocks[b_idx])),
            "Принято с шумом": "".join(map(str, rec_block)),
            "Синдром (S)": f"{bin(syn)[2:].zfill(3)} (поз. {err_pos})" if syn else "000 (0)",
            "Статус декодера": status,
            "Восстановлено": "".join(map(str, corr_block)),
        }
    )

# Сборка финального текста
raw_text = nibbles_to_text(raw_received_nibbles)
restored_text = nibbles_to_text(restored_nibbles)
total_injected_noise = sum(st.session_state.noise_mask)

st.subheader("3. Результаты приема и восстановления")

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Всего бит в канале", total_bits)
m_col2.metric("Внесено ошибок", f"{total_injected_noise} бит")
m_col3.metric("Обнаружено и устранено", f"{total_errors_detected} блоков")
m_col4.metric(
    "Целостность данных",
    "100%" if restored_text == user_text else "Сбой (>1 ошибки на блок)",
)

# Сравнение текста на экранах
res_col1, res_col2, res_col3 = st.columns(3)
with res_col1:
    st.success(f"**1. Исходный текст:**\n### {user_text}")
with res_col2:
    st.error(f"**2. Текст без защиты (с шумом):**\n### {raw_text}")
with res_col3:
    st.info(f"**3. Восстановленный Хэммингом:**\n### {restored_text}")

# Детальный отчет по кодовым словам
st.subheader("📊 Пошаговый отчет декодера по каждому блоку")
st.dataframe(pd.DataFrame(report_data), use_container_width=True)

with st.expander("📘 Теоретическая справка для ответа на защите"):
    st.markdown(
        """
    * **Код Хэмминга (7,4)** — блочный систематический помехоустойчивый код, который на каждые **4 информационных бита** добавляет **3 проверочных бита** паритета.
    * **Кодовое расстояние:** $d_{\\min} = 3$. Это гарантирует обнаружение до 2 ошибок или гарантированное **исправление 1 ошибки** в каждом 7-битном слове.
    * **Синдром ошибки ($S$):** рассчитывается через проверку четности проверочными матрицами:
      * $s_1 = r_1 \\oplus r_3 \\oplus r_5 \\oplus r_7$
      * $s_2 = r_2 \\oplus r_3 \\oplus r_6 \\oplus r_7$
      * $s_3 = r_4 \\oplus r_5 \\oplus r_6 \\oplus r_7$
    * Двоичное число $(s_3 s_2 s_1)_2$ прямо указывает на порядковый номер искаженного бита. Если синдром равен `000`, ошибок в блоке нет.
    """
    )
