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
        "Welcome to the MBA Tracking application bot!\n"
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
    await message.answer(
        f"Thank you for your personal info. Now let's move to the Motivation Letter Questions.\n\n"
        f"Q1: Why do you want to join the MBA Tracking program? What motivates you to become a part of this program?\n{WARNING_TEXT}"
    )
    await state.set_state(ApplicationForm.q1)

@router.message(ApplicationForm.q1)
async def process_q1(message: Message, state: FSMContext):
    if not message.text or len(message.text) < 5:
        await message.answer("Please provide a more detailed answer.")
        return
    await state.update_data(q1=message.text)
    await message.answer(
        f"Q2: What is your main reason for applying to this program at this stage of your life?\n{WARNING_TEXT}"
    )
    await state.set_state(ApplicationForm.q2)

@router.message(ApplicationForm.q2)
async def process_q2(message: Message, state: FSMContext):
    if not message.text or len(message.text) < 5:
        await message.answer("Please provide a more detailed answer.")
        return
    await state.update_data(q2=message.text)
    await message.answer(
        f"Q3: What are three key skills you would like to develop through the MBA Tracking program? Please explain why these skills are important for your personal or professional growth.\n{WARNING_TEXT}"
    )
    await state.set_state(ApplicationForm.q3)

@router.message(ApplicationForm.q3)
async def process_q3(message: Message, state: FSMContext):
    if not message.text or len(message.text) < 5:
        await message.answer("Please provide a more detailed answer.")
        return
    await state.update_data(q3=message.text)
    await message.answer(
        f"Q4: Where do you see yourself in five years? What are your main career and personal goals?\n{WARNING_TEXT}"
    )
    await state.set_state(ApplicationForm.q4)

@router.message(ApplicationForm.q4)
async def process_q4(message: Message, state: FSMContext):
    if not message.text or len(message.text) < 5:
        await message.answer("Please provide a more detailed answer.")
        return
    await state.update_data(q4=message.text)
    await message.answer(
        f"Q5: Tell us about your experience of working in a team. What role do you usually take when working with others, and what have you learned from your teamwork experience?\n{WARNING_TEXT}"
    )
    await state.set_state(ApplicationForm.q5)

@router.message(ApplicationForm.q5)
async def process_q5(message: Message, state: FSMContext, bot: Bot):
    if not message.text or len(message.text) < 5:
        await message.answer("Please provide a more detailed answer.")
        return
    await state.update_data(q5=message.text)
    data = await state.get_data()
    
    # Send Final Message to User
    await message.answer("Thank you for completing the application! Our team will review your submission and contact you soon.")
    
    # Format submission for Admin
    username = f"@{message.from_user.username}" if message.from_user.username else "No username"
    user_id = message.from_user.id
    
    admin_text = (
        f"🆕 <b>New MBA Tracking Application</b>\n\n"
        f"👤 <b>Personal Info:</b>\n"
        f"Name: {data.get('full_name')}\n"
        f"Phone: {data.get('phone_number')}\n"
        f"English Level: {data.get('english_level')}\n"
        f"Region: {data.get('region')}\n"
        f"Telegram: {username} (ID: {user_id})\n\n"
        f"📝 <b>Motivation Letter:</b>\n"
        f"<b>Q1:</b> {data.get('q1')}\n\n"
        f"<b>Q2:</b> {data.get('q2')}\n\n"
        f"<b>Q3:</b> {data.get('q3')}\n\n"
        f"<b>Q4:</b> {data.get('q4')}\n\n"
        f"<b>Q5:</b> {data.get('q5')}"
    )
    
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
