import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import mysql.connector as sql
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt
import re

mobile_number = ""
# Ensure that the target directory exists, and create it if it doesn't
target_directory = os.path.join(os.getcwd(), "uploaded_cards")
if not os.path.exists(target_directory):
    os.makedirs(target_directory)


uploaded_card = st.file_uploader("Upload a card", type=["png", "jpeg", "jpg"])
# Check if a card has been uploaded and save it
if uploaded_card is not None:
    def save_card(uploaded_card):
        file_path = os.path.join(target_directory, uploaded_card.name)
        with open("uploaded_card.jpg", "wb") as f:
            f.write(uploaded_card.getbuffer())

    # Call the save_card function to save the uploaded card
    save_card(uploaded_card)

# SETTING-UP BACKGROUND IMAGE
def setting_bg():
    st.markdown(f""" 
    <style>
        .stApp {{
            background: linear-gradient(to right, #2b5876, #4e4376);
            background-size: cover;
            transition: background 0.5s ease;
        }}
        h1,h2,h3,h4,h5,h6 {{
            color: #f3f3f3;
            font-family: 'Roboto', sans-serif;
        }}
        .stButton>button {{
            color: #4e4376;
            background-color: #f3f3f3;
            transition: all 0.3s ease-in-out;
        }}
        .stButton>button:hover {{
            color: #f3f3f3;
            background-color: #2b5876;
        }}
        .stTextInput>div>div>input {{
            color: #4e4376;
            background-color: #f3f3f3;
        }}
    </style>
    """, unsafe_allow_html=True)

setting_bg()

# CREATING OPTION MENU
selected = option_menu(None, ["Home", "Upload & Extract", "Modify"],
                       icons=["home", "cloud-upload-alt", "edit"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "25px", "text-align": "center", "margin": "0px",
                                            "--hover-color": "#AB63FA",
                                            "transition": "color 0.3s ease, background-color 0.3s ease"},
                               "icon": {"font-size": "25px"},
                               "container": {"max-width": "6000px", "padding": "10px", "border-radius": "5px"},
                               "nav-link-selected": {"background-color": "#AB63FA", "color": "white"}})

# INITIALIZING THE EasyOCR READER
reader = easyocr.Reader(['en'])

# CONNECTING WITH MYSQL DATABASE
mydb = sql.connect(host="localhost",
                   user="root",
                   password="Aaru@123user",
                   database="bizcardx_db"
                   )
mycursor = mydb.cursor(buffered=True)
#mycursor.execute("create database bizcardx_db")

# TABLE CREATION
mycursor.execute('''CREATE TABLE IF NOT EXISTS card_data
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    company_name TEXT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code VARCHAR(10),
                    image LONGBLOB
                    )''')
# HOME MENU
if selected == "Home":
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("## :blue[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
        st.markdown(
            "## :blue[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")
    with col2:
        st.image("home.jpg")

# UPLOAD AND EXTRACT MENU
if selected == "Upload & Extract":
    #st.markdown("### Upload a Business Card")
    #uploaded_card = st.file_uploader("upload here", label_visibility="collapsed", type=["png", "jpeg", "jpg"])

    target_directory = "uploaded_cards"
    result = []
    if uploaded_card is not None:
        saved_img = os.path.join(target_directory, uploaded_card.name)
        result = reader.readtext(saved_img, detail=0, paragraph=False)

        def save_card(uploaded_card):
            with open(os.path.join("uploaded_cards", uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())


        save_card(uploaded_card)
        # Load the image using Pillow (PIL)
        uploaded_image = Image.open("uploaded_card.jpg")

        # Display the uploaded image
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)


        def image_preview(image, res):
            for (bbox, text, prob) in res:
                # unpack the bounding box
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            plt.rcParams['figure.figsize'] = (15, 15)
            plt.axis('off')
            img_height, img_width, _ = image.shape
            img = cv2.resize(img, (int(model_height * ratio), model_height), interpolation=cv2.INTER_LINEAR)
            plt.imshow(img)



        # DISPLAYING THE UPLOADED CARD
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("#     ")
            st.markdown("### You have uploaded the card")
            st.image(uploaded_card)
        # DISPLAYING THE CARD WITH HIGHLIGHTS
        with col2:
            st.markdown("#     ")
            st.markdown("#     ")
            with st.spinner("Please wait processing image..."):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_img = os.getcwd() + "\\" + "uploaded_cards" + "\\" + uploaded_card.name
                image = Image.open(saved_img)
                res = reader.readtext(saved_img)
                st.markdown("### Image Processed and Data Extracted")
                st.image(image)

                # easy OCR
        #saved_img = os.getcwd() + "\\" + "uploaded_cards" + "\\" + uploaded_card.name
        result = reader.readtext(saved_img, detail=0, paragraph=False)


        # CONVERTING IMAGE TO BINARY TO UPLOAD TO SQL DATABASE
        def img_to_binary(file):
            with open(file, 'rb') as file:
                binary_data = file.read()
            return binary_data


        saved_img = os.getcwd() + "\\" + "uploaded_cards" + "\\" + uploaded_card.name
        binary_image = img_to_binary(saved_img)


        data = {"company_name": [],
                "card_holder": [],
                "designation": [],
                "mobile_number":[],  # Initialize mobile_number
                "email": [],
                "website": [],
                "area": [],
                "city": [],
                "state": [],
                "pin_code": [],
                "image": binary_image
                }


    def get_data(res):
        global mobile_number  # Declare mobile_number as a global variable
        # Initialize the data dictionary
        data = {
            "company_name": "",
            "card_holder": "",
            "designation": "",
            "mobile_number": "",  # Initialize mobile_number as an empty string
            "email": "",
            "website": "",
            "area": "",
            "city": "",
            "state": "",
            "pin_code": "",
        }

        for ind, i in enumerate(res):
            if "www " in i.lower() or "www." in i.lower():
                data["website"] = i
            elif "@" in i:
                data["email"] = i
                if "-" in i:
                    if "mobile_number" not in data:
                        data["mobile_number"] = i
                    else:
                        data["mobile_number"] += f" & {i}"
            elif ind == len(res) - 1:
                data["company_name"] = i
            elif ind == 0:
                data["card_holder"] = i
            elif ind == 1:
                data["designation"] = i

            if re.findall('^[0-9].+, [a-zA-Z]+', i):
                data["area"] = i.split(',')[0]
            elif re.findall('[0-9] [a-zA-Z]+', i):
                data["area"] = i

            match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
            match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
            match3 = re.findall('^[E].*', i)
            if match1:
                data["city"] = match1[0]
            elif match2:
                data["city"] = match2[0]
            elif match3:
                data["city"] = match3[0]

            state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
            if state_match:
                data["state"] = i[:9]
            elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                data["state"] = i.split()[-1]

            if len(i) >= 6 and i.isdigit():
                data["pin_code"] = i
            elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                data["pin_code"] = i[10:]

        # Update the global mobile_number variable
        mobile_number = data["mobile_number"]

        return data


    def create_df(extracted_data):
        df = pd.DataFrame([extracted_data])  # Wrap 'data' in a list to create a DataFrame
        return df


    extracted_data = get_data(result)
    df = create_df(extracted_data)

# ...
if st.button("Upload to Database"):
    for i, row in df.iterrows():
        try:
            query = """
                    INSERT INTO card_data(
                        company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code, image
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
            if 'image' in df.columns:
                image = row['image']
            else:
                image = None  # Handle the case where 'image' column is not present

            mycursor.execute(query, (
                row["company_name"], row["card_holder"], row["designation"], row["mobile_number"],
                row["email"], row["website"], row["area"], row["city"], row["state"], row["pin_code"], image
            ))
            mydb.commit()
        except sql.Error as e:
            st.error(f"Error uploading to database: {e}")
            st.success("#### Uploaded to database successfully!")
    st.write("Extracted Information:")
    st.write(extracted_data)
# ...

# MODIFY MENU
if selected == "Modify":
    col1, col2, col3 = st.columns([3, 3, 2])
    col2.markdown("## Alter or Delete the data here")
    column1, column2 = st.columns(2, gap="large")
    try:
        with column1:
            mycursor.execute("SELECT card_holder FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]

            print(business_cards)  # Print the business cards dictionary to check the values

            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycursor.execute(
                "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data WHERE card_holder=%s",
                (selected_card,))
            result = mycursor.fetchone()

            # DISPLAYING ALL THE INFORMATIONS
            company_name = st.text_input("Company_Name", result[0])
            card_holder = st.text_input("Card_Holder", result[1])
            designation = st.text_input("Designation", result[2])
            mobile_number = st.text_input("Mobile_Number", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            area = st.text_input("Area", result[6])
            city = st.text_input("City", result[7])
            state = st.text_input("State", result[8])
            pin_code = st.text_input("Pin_Code", result[9])

            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycursor.execute("""UPDATE card_data SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                                    WHERE card_holder=%s""", (
                company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code,
                selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")

        with column2:
            mycursor.execute("SELECT card_holder FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :blue[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")

            if st.button("Yes Delete Business Card"):
                mycursor.execute(f"DELETE FROM card_data WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
    except:
        st.warning("There is no data available in the database")

    if st.button("View updated data"):
        mycursor.execute(
            "SELECT company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code FROM card_data")
        updated_df = pd.DataFrame(mycursor.fetchall(),
                                  columns=["Company_Name", "Card_Holder", "Designation", "Mobile_Number", "Email",
                                           "Website", "Area", "City", "State", "Pin_Code"])
        st.write(updated_df)


if __name__ == "__main__":
    st.title("BizCardX: Extracting Business Card Data with OCR")
    st.sidebar.title("Sidebar")
