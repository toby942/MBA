from aiogram import F
from database import save_lead, get_user_id

GROUP_CHAT_ID = -1004452685432
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from states import ApplicationForm, AdminReply
from keyboards import get_contact_keyboard, get_english_level_keyboard
import config

router = Router()

WARNING_TEXT = "(Note: Please do not use AI to generate your answers)."

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    welcome_text = (
        "Welcome to the MBA Trucking application bot!\n"
        "Let's start with your personal information.\n\n"
        "Please enter your Full Name (Ism va Familiya):"
    )
    await message.answer(welcome_text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(ApplicationForm.full_name)

@router.message(ApplicationForm.full_name)
async def process_full_name(message: Message, state: FSMContext):
    if not message.text or len(message.text) < 3:
        await message.answer("Please enter a valid full name (at least 3 characters).")
        return
    
    await state.update_data(full_name=message.text)
    await message.answer(
        "Great! Now please share your Phone Number (or type it manually):",
        reply_markup=get_contact_keyboard()
    )
    await state.set_state(ApplicationForm.phone_number)

@router.message(ApplicationForm.phone_number)
async def process_phone_number(message: Message, state: FSMContext):
    phone = ""
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text
    else:
        await message.answer("Please share your contact using the button or type your phone number.")
        return
        
    await state.update_data(phone_number=phone)
    # Remove reply keyboard
    msg = await message.answer("Saving your number...", reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    
    await message.answer(
        "Thank you! What is your English Proficiency Level?",
        reply_markup=get_english_level_keyboard()
    )
    await state.set_state(ApplicationForm.english_level)

@router.callback_query(ApplicationForm.english_level, F.data.startswith("eng_"))
async def process_english_level(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    await state.update_data(english_level=level)
    await callback.message.edit_text(f"English Proficiency Level: {level}")
    await callback.message.answer("Where do you live? Please enter your Region/City of Residence (Qaysi hududda yashaysiz?):")
    await state.set_state(ApplicationForm.region)

@router.message(ApplicationForm.region)
async def process_region(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Please enter your Region/City as text.")
        return
        
    await state.update_data(region=message.text)
    import random

PAIN_QUESTIONS = [
    "1. How serious is your intention to start a career in the US logistics market?",
    "2. Why did you choose this industry specifically? Have you ever started another path before and failed to finish?",
    "3. Does the fear of not knowing English or struggling with communication hold you back from entering this field?",
    "4. Is your current income or job satisfying you? If not, what is the exact reason?",
    "5. Does the pressure from family or loved ones expecting your financial situation to improve weigh heavily on you?",
    "6. What do you think has mainly caused you to fail or get no results from studying online before?",
    "7. What scares you the most in this industry: wasting time or losing money?",
    "8. If you don't change anything in the next 2 months, what scares you most about staying in the same place?",
    "9. Have you ever bought similar online courses before and failed to finish them? Why did you quit?",
    "10. Do you want to break free from depending on others daily and finally run your own business or career?",
    "11. What are your main quality standards for education, and what do you fear others might deceive you with?",
    "12. Do you worry that if you face difficulties or don't understand something during your studies, you'll be left completely alone without help?",
    "13. Is not having 2-3 hours a day for learning a real excuse, or are you genuinely too busy?",
    "14. Have you ever hesitated to spend money on self-development or had to study secretly from your family?",
    "15. Aren't you exhausted from searching for a structured course that actually delivers real results?",
    "16. Are you afraid that US companies will reject you after graduation because you 'lack experience'?",
    "17. What push or trigger do you feel you are missing to fundamentally change your current financial situation?",
    "18. If you fail to achieve results this time as well, what will your next step or plan be?",
    "19. Are you ready to leave your phone number so our managers can help you overcome your doubts and fears?",
    "20. In your opinion, what is the very first thing a person must do to achieve true success?"
]

# Ingliz tili darajasi tanlangandan so'ng ishga tushadigan qism:
@router.callback_query(ApplicationForm.english_level)
async def process_english_level(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    await state.update_data(english_level=level)
    
    # 20 ta savoldan tasodifiy 3 tasini tanlaymiz
    selected_questions = random.sample(PAIN_QUESTIONS, 3)
    await state.update_data(questions=selected_questions, current_index=0, user_answers=[])
    
    await callback.message.edit_text(f"English Level: {level}")
    
    # 1-savolni yuboramiz
    first_q = selected_questions[0]
    await callback.message.answer(f"Ajoyib! Endi 3 ta savolga javob berasiz (1/3):\n\n{first_q}")
    await state.set_state(ApplicationForm.answering_questions)

# Tasodifiy savollarga ketma-ket javob olish
@router.message(ApplicationForm.answering_questions)
async def process_pain_answers(message: Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get("questions")
    index = data.get("current_index")
    answers = data.get("user_answers", [])
    
    answers.append(message.text)
    index += 1
    
    if index < len(questions):
        await state.update_data(current_index=index, user_answers=answers)
        next_q = questions[index]
        await message.answer(f"Savol ({index+1}/3):\n\n{next_q}")
    else:
        # 3 ta savol tugadi, endi guruhga yuboramiz
        user_data = await state.get_data()
        
        admin_text = (
            f"<b>New MBA Tracking Application!</b>\n\n"
            f"<b>Personal Info:</b>\n"
            f"Name: {user_data.get('full_name')}\n"
            f"Phone: {user_data.get('phone_number')}\n"
            f"English Level: {user_data.get('english_level')}\n"
            f"Region: {user_data.get('region')}\n"
            f"Telegram: @{message.from_user.username} (ID: {message.from_user.id})\n\n"
            f"<b>Random Pain Questions & Answers:</b>\n"
        )
        
        for i in range(3):
            admin_text += f"\n<b>Q{i+1}:</b> {questions[i]}\n<b>A{i+1}:</b> {answers[i]}\n"
            
        if config.ADMIN_CHAT_ID:
            try:
                reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Reply to Applicant", callback_data=f"reply_{message.from_user.id}")]
                ])
                sent_msg = await message.bot.send_message(
                    chat_id=config.ADMIN_CHAT_ID,
                    text=admin_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
                # Bazaga guruh xabari va user_id ni saqlaymiz (oldingi database.py dagi funksiya)
                save_lead(sent_msg.message_id, message.from_user.id)
            except Exception as e:
                print(f"Failed to send application to admin: {e}")
                
        await message.answer("Thank you for completing the application! Our team will review your submission and contact you soon.")
        await state.clear()
    if config.ADMIN_CHAT_ID:
        try:
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💬 Reply to Applicant", callback_data=f"reply_{user_id}")]
            ])
            await bot.send_message(
                chat_id=config.ADMIN_CHAT_ID,
                text=admin_text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Failed to send application to admin: {e}")
            
    await state.clear()

@router.callback_query(F.data.startswith("reply_"))
async def process_reply_button(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split("_")[1]
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminReply.waiting_for_reply)
    await callback.message.reply("✏️ Iltimos, foydalanuvchiga yubormoqchi bo'lgan xabaringizni kiriting:")
    await callback.answer()

@router.message(AdminReply.waiting_for_reply)
async def process_admin_reply_message(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    
    if not target_user_id:
        await message.answer("Xatolik: Foydalanuvchi topilmadi.")
        await state.clear()
        return

    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=f"📩 <b>Adminstratsiyadan xabar:</b>\n\n{message.text}",
            parse_mode="HTML"
        )
        await message.answer("✅ Xabaringiz foydalanuvchiga muvaffaqiyatli yuborildi.")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi, foydalanuvchiga xabar bormadi: {e}")
    finally:
        await state.clear()
@router.message(F.chat.id == GROUP_CHAT_ID)
async def manager_reply_handler(message: Message):
    # Agar menejer guruhdagi xabarga Reply (javob) qilgan bo'lsa
    if message.reply_to_message:
        replied_msg_id = message.reply_to_message.message_id
        target_user_id = get_user_id(replied_msg_id)
        
        if target_user_id:
            try:
                # Menejerning matnini to'g'ridan-to'g'ri mijozga yuboramiz
                await message.bot.send_message(
                    target_user_id, 
                    f"💬 **Menejer javobi:**\n\n{message.text}"
                )
                await message.reply("✅ Javob mijozga yetkazildi!")
            except Exception as e:
                await message.reply(f"❌ Xatolik: {e}")
                # Guruhga yuboriladigan xabar
lead_text = (
            f"🚨 **Yangi Lid (Ariza)!**\n\n"
            f"👤 **Foydalanuvchi:** @{message.from_user.username} ({message.from_user.full_name})\n"
            f"🆔 **User ID:** `{message.from_user.id}`\n\n"
            f"📝 Foydalanuvchi barcha savollarga javob berdi."
        )
        sent_msg = await message.bot.send_message(GROUP_CHAT_ID, lead_text, parse_mode="Markdown")
        save_lead(sent_msg.message_id, message.from_user.id)