import random
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import config
from database import save_lead
from states import LeadForm, AdminReply

router = Router()
# yangilash
# Pool of 20 randomized questions for the lead form
QUESTIONS_POOL = [
    "What is your primary goal for joining this program?",
    "How many years of professional experience do you have?",
    "Describe a time you demonstrated leadership.",
    "What are your expectations from this MBA?",
    "How do you handle conflict in a team?",
    "What is your greatest professional achievement?",
    "Where do you see your career in 5 years?",
    "Why did you choose our program specifically?",
    "How do you plan to balance work and studies?",
    "What unique skills do you bring to a cohort?",
    "Describe a challenge you overcame at work.",
    "What industry are you most interested in?",
    "How do you define successful teamwork?",
    "Discuss a recent business trend that interests you.",
    "Who is a leader you admire and why?",
    "What is your approach to problem-solving?",
    "How do you stay updated with industry news?",
    "What motivates you to perform your best?",
    "Describe a time you had to pivot your strategy.",
    "What is your long-term entrepreneurial vision?"
]


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    
    # Randomly sample 3 distinct questions from the pool
    selected_questions = random.sample(QUESTIONS_POOL, 3)
    
    # Store them in FSM context
    await state.update_data(questions=selected_questions)
    
    await message.answer(
        "Welcome! Let's start your application.\nPlease enter your full name:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(LeadForm.full_name)

@router.message(LeadForm.full_name)
async def process_full_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Please enter a valid full name.")
        return

    await state.update_data(full_name=message.text)
    await message.answer("Please enter your phone number:")
    await state.set_state(LeadForm.phone_number)


@router.message(LeadForm.phone_number)
async def process_phone_number(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Please enter a valid phone number.")
        return

    await state.update_data(phone_number=message.text)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Beginner", callback_data="level_Beginner")],
        [InlineKeyboardButton(text="Intermediate", callback_data="level_Intermediate")],
        [InlineKeyboardButton(text="Advanced", callback_data="level_Advanced")],
    ])
    await message.answer("What is your English level?", reply_markup=keyboard)
    await state.set_state(LeadForm.english_level)


@router.callback_query(F.data.startswith("level_"), LeadForm.english_level)
async def process_english_level(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    await state.update_data(english_level=level)

    await callback.message.edit_text(f"English level: {level} ✅")
    await callback.message.answer("Please enter your Region/City:")
    await state.set_state(LeadForm.region)
    await callback.answer()
@router.message(LeadForm.region)
async def process_region(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Please enter a valid text for your region.")
        return

    await state.update_data(region=message.text)
    data = await state.get_data()
    questions = data.get("questions", [])

    await message.answer(f"Question 1: {questions[0]}")
    await state.set_state(LeadForm.q1)


@router.message(LeadForm.q1)
async def process_q1(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Please provide a text answer.")
        return

    await state.update_data(a1=message.text)
    data = await state.get_data()
    questions = data.get("questions", [])

    await message.answer(f"Question 2: {questions[1]}")
    await state.set_state(LeadForm.q2)


@router.message(LeadForm.q2)
async def process_q2(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Please provide a text answer.")
        return

    await state.update_data(a2=message.text)
    data = await state.get_data()
    questions = data.get("questions", [])

    await message.answer(f"Question 3: {questions[2]}")
    await state.set_state(LeadForm.q3)


@router.message(LeadForm.q3)
async def process_q3(message: Message, state: FSMContext, bot: Bot):
    if not message.text:
        await message.answer("Please provide a text answer.")
        return

    await state.update_data(a3=message.text)
    data = await state.get_data()
    
    # Send completion message to user
    await message.answer(
        "Thank you for completing the application! "
        "Our team will review your submission and contact you soon."
    )
    
    # Build Admin Summary
    user = message.from_user
    full_name = data.get("full_name", user.full_name)
    phone_number = data.get("phone_number", "N/A")
    english_level = data.get("english_level", "N/A")
    username = f"@{user.username}" if user.username else "No Username"
    user_id = user.id
    
    region = data.get("region", "N/A")
    questions = data.get("questions", [])
    a1 = data.get("a1", "")
    a2 = data.get("a2", "")
    a3 = data.get("a3", "")

    admin_text = (
        f"🆕 <b>New Lead Application</b>\n\n"
        f"👤 <b>Applicant Info:</b>\n"
        f"Name: {full_name}\n"
        f"Phone: {phone_number}\n"
        f"English Level: {english_level}\n"
        f"Username: {username}\n"
        f"Telegram ID: <code>{user_id}</code>\n"
        f"Region: {region}\n\n"
        f"📝 <b>Q&A:</b>\n"
        f"<b>Q1:</b> {questions[0]}\n"
        f"<b>A1:</b> {a1}\n\n"
        f"<b>Q2:</b> {questions[1]}\n"
        f"<b>A2:</b> {a2}\n\n"
        f"<b>Q3:</b> {questions[2]}\n"
        f"<b>A3:</b> {a3}"
    )

    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Reply to Applicant", callback_data=f"reply_{user_id}")]
    ])

    try:
        sent_msg = await bot.send_message(
            chat_id=config.GROUP_CHAT_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        # Execute database function
        save_lead(sent_msg.message_id, user_id)
    except Exception as e:
        print(f"Failed to send application to group chat: {e}")
        
    await state.clear()


@router.callback_query(F.data.startswith("reply_"))
async def process_reply_button(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split("_")[1]
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminReply.waiting_for_reply)
    await callback.message.reply("✏️ Please enter the message you want to send to the applicant:")
    await callback.answer()


@router.message(AdminReply.waiting_for_reply)
async def process_admin_reply_message(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    
    if not target_user_id:
        await message.answer("Error: Target user not found.")
        await state.clear()
        return

    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=f"📩 <b>Message from Administration:</b>\n\n{message.text}",
            parse_mode="HTML"
        )
        await message.answer("✅ Your message was successfully sent to the applicant.")
    except Exception as e:
        await message.answer(f"❌ Failed to send message to applicant: {e}")
    finally:
        await state.clear()
