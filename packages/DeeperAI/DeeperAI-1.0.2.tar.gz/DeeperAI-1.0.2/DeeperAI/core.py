import os
from rich import print as pr
pr("[bold red] [+] [/bold red][bold yellow] Start DeeperAi... [/bold yellow]")

import requests, json, re, time, random, serial, torch, nltk, joblib, spacy, time, sys, numpy as np,  matplotlib.pyplot as plt, cv2
from math import cos, sin, radians, sqrt, degrees, atan2
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
from googlesearch import search
from PIL import Image
from torch.utils.data import TensorDataset
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments
from transformers import AutoModelForCausalLM, AutoTokenizer
from langdetect import detect
from textblob import TextBlob
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from transformers import DistilBertTokenizer, DistilBertModel, GPT2LMHeadModel, GPT2Tokenizer
from transformers import (RobertaTokenizer, RobertaForSequenceClassification, 
                            T5Tokenizer, T5ForConditionalGeneration, 
                            BertTokenizer, BertForSequenceClassification, 
                            GPT2Tokenizer, GPT2LMHeadModel,
                            XLNetTokenizer, XLNetForSequenceClassification)
from scipy.stats import multivariate_normal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as firefox_option_driver
firefox_option = firefox_option_driver()
firefox_option.add_argument("--headless")
from selenium.webdriver.edge.options import Options as edge_option_driver
edge_option = edge_option_driver()
edge_option.add_argument("--headless")
from selenium.webdriver.ie.options import Options as ie_option_driver
ie_option = ie_option_driver()
ie_option.add_argument("--headless")
from selenium.webdriver.chrome.options import Options as chrome_option_driver
chrome_option = chrome_option_driver()
chrome_option.add_argument("--headless")


# Ensure nltk resources are downloaded
nltk.download('punkt')

pr("[bold red] [+] [/bold red][bold yellow] Finish. [/bold yellow]")
pr("[bold red] [+] [/bold red][bold yellow] Running... [/bold yellow]")




















class Narrow_AI:


    class DataCreator:



        

        class WebScraper:



            def scrape_website(base_url,data_file):
                def is_same_domain(base_url, url):
                    base_domain = urlparse(base_url).netloc
                    url_domain = urlparse(url).netloc
                    return base_domain == url_domain
                visited = set()  # برای نگه‌داری صفحات بازدید شده
                to_visit = [base_url]  # صفحاتی که باید بازدید شوند

                # اگر فایل موجود باشد، پاک کردن محتوا
                if os.path.exists(data_file):
                    os.remove(data_file)

                while to_visit:
                    current_url = to_visit.pop(0)
                    if current_url in visited:
                        continue
                    visited.add(current_url)

                    try:
                        response = requests.get(current_url, timeout=10)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.text, 'html.parser')

                        # ذخیره متن صفحه در فایل
                        with open(data_file, "a", encoding="utf-8") as f:
                            f.write(f"URL: {current_url}\n")
                            f.write(soup.get_text(separator="\n").strip())
                            f.write("\n\n" + "-"*50 + "\n\n")

                        # پیدا کردن لینک‌های جدید
                        for link in soup.find_all("a", href=True):
                            href = link['href']
                            absolute_url = urljoin(base_url, href)  # ساخت لینک کامل
                            if is_same_domain(base_url, absolute_url) and absolute_url not in visited:
                                to_visit.append(absolute_url)

                    except Exception as e:
                        print(f"Error scraping {current_url}: {e}")






            class CodeGenerator:
                def __init__(self, query):
                    self.query = query
                    self.results = []
                    self.first_url = None

                def perform_search(self):
                    """Perform a Google search and store the results."""
                    self.results = list(search(self.query, num=10))
                    if not self.results:
                        print("Null")
                        return
                    self.first_url = self.results



                def fetch_site_content(self):
                    def extract_code_or_summary(self, html_content):
                        """Extract code blocks or a summary from the HTML content."""
                        soup = BeautifulSoup(html_content, 'html.parser')
                        code_blocks = soup.find_all(['code', 'pre'])
                        
                        out=""
                        if code_blocks:
                            for code in code_blocks:
                                out=(f"""{out}
    {code.get_text()}""")
                            return (out)
                        else:
                            self.extract_summary(soup)

                    def extract_summary(self, soup):
                        """Extract a summary from the site if no code blocks are found."""
                        paragraphs = soup.find_all('p')
                        if paragraphs:
                            return(paragraphs[0].get_text())
                        else:
                            return None

                    if not self.first_url:
                        print("Please Search")
                        return
                    for nurl in self.first_url:
                        try:
                            response = requests.get(self.first_url)
                            response.raise_for_status()
                            return response.text
                        except requests.RequestException as e:
                            print(f"Error Connect: {e}")
                            return None



                def run(self):
                    """Run the web scraper."""
                    self.perform_search()
                    html_content = self.fetch_site_content()
                    if html_content:
                        return (self.extract_code_or_summary(html_content))
                    else:
                        return(None)
                    


            
            def PhotoGenerator(text, output_name, model_name='DreamShaper 8'):
                XPATHS = {
                        "text_area": "/html/body/div[3]/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div/div/textarea",
                        "run_button": "/html/body/div[3]/div/div[2]/div/div/div[2]/div[2]/button",
                        "image_output": "image-output"
                        }
                driver = webdriver.Firefox()
                def wait_full_xpath(xp):
                    while True:
                        try:
                            driver.find_element(By.XPATH,xp)
                            break
                        except:
                            time.sleep(3)
                def wait_full_id(x):
                    while True:
                        try:
                            driver.find_element(By.ID,x)
                            break
                        except:
                            time.sleep(3)
                driver.get("https://dezgo.com/txt2img")
                wait_full_xpath("/html/body/div[3]/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div/div/textarea")
                wait_full_xpath("/html/body/div[3]/div/div[2]/div/div/div[2]/div[2]/button")
                driver.find_element(By.XPATH,"/html/body/div[3]/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div/div/textarea").send_keys(text)
                driver.find_element(By.XPATH,"/html/body/div[3]/div/div[2]/div/div/div[2]/div[2]/button").click()
                wait_full_id("image-output")
                driver.find_element(By.ID, "image-output").screenshot(filename=output_name)
                driver.quit()






        class InternetDataScanner:
            def __init__(MainWords,GetForOne,Output_File_Name,ReSearch=False,logs=True):
                def get_search_results(query):
                    return list(search(query, num=int(GetForOne)))

                def scrape_text_from_url(url):
                    try:
                        response = requests.get(url)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        # استخراج متن از تگ‌های <p>
                        paragraphs = soup.find_all('p')
                        text_content = ' '.join(p.get_text() for p in paragraphs)
                        return text_content
                    except Exception as e:
                        print(f"Error fetching {url}: {e}")
                        return ""
                try:
                    open(Output_File_Name)
                except:
                    open(Output_File_Name,'w+')
                
                # باز کردن فایل Data.txt برای ذخیره محتوا
                with open(Output_File_Name, 'w+', encoding='utf-8') as data_file:
                    for word in MainWords:
                        if logs==True:print(f"Search Word : {word}")
                        urls = get_search_results(word)
                        for url in urls:
                            if logs==True:print(f"Open Site : {url}")
                            text_content = scrape_text_from_url(url)
                            if text_content:
                                data_file.write(text_content + '\n')
                            time.sleep(1)

                if ReSearch==True:
                    # باز کردن فایل و جستجوی مجدد در گوگل
                    with open(Output_File_Name, 'r', encoding='utf-8') as data_file:
                        all_text = data_file.read()
                        additional_words = all_text.split()  # فقط ۱۰ کلمه اول را برای جستجو در نظر می‌گیریم

                    for word in additional_words:
                        if logs==True:print(f"ReSearch {word}")
                        urls = get_search_results(word)
                        with open(Output_File_Name, 'a+', encoding='utf-8') as additional_file:
                            for url in urls:
                                if logs==True:print(f"Open Site : {url}")
                                text_content = scrape_text_from_url(url)
                                if text_content:
                                    additional_file.write(text_content + '\n')
                                time.sleep(1)  # برای جلوگیری از بارگذاری بیش از حد در سرور


    



    class RootTools:

        class NLP:


            def __init__(self, text):
                self.text = text
                self.tokens = []
                self.cleaned_text = ""
                
            def tokenize(self):
                """تجزیه متن به توکن‌ها."""
                nltk.download('punkt')
                self.tokens = nltk.word_tokenize(self.text)
                return self.tokens

            def clean_text(self):
                """پاکسازی متن از نشانه‌ها و کاراکترهای خاص."""
                self.cleaned_text = re.sub(r'[^\w\s]', '', self.text)
                return self.cleaned_text

            def count_words(self):
                """شمارش تعداد کلمات در متن."""
                return len(self.tokens)

            def word_frequency(self):
                """محاسبه فراوانی کلمات."""
                return Counter(self.tokens)

            def detect_language(self):
                """تشخیص زبان متن (به صورت ساده)."""
                return detect(self.text)

            def sentiment_analysis(self):
                """تحلیل احساسات متن."""
                analysis = TextBlob(self.text)
                return {
                    "polarity": analysis.sentiment.polarity,
                    "subjectivity": analysis.sentiment.subjectivity
                }

            def named_entity_recognition(self):
                """تشخیص موجودیت‌های نامدار."""
                nlp = spacy.load("fa_core_news_sm")
                doc = nlp(self.text)
                return [(ent.text, ent.label_) for ent in doc.ents]

            def lemmatize(self):
                """تبدیل به نرمال (lemmatization)."""
                nlp = spacy.load("fa_core_news_sm")
                doc = nlp(self.text)
                return [token.lemma_ for token in doc]

            def sentence_length_analysis(self):
                """تحلیل طول جملات."""
                sentences = nltk.sent_tokenize(self.text)
                return [len(sentence.split()) for sentence in sentences]

            def analyze_multiple_texts(self, texts):
                """تحلیل چندین متن مختلف و ایجاد منبع یادگیری به فرمت JSON."""
                results = []
                for text in texts:
                    self.text = text
                    self.tokenize()
                    self.clean_text()
                    result = {
                        "original_text": text,
                        "cleaned_text": self.cleaned_text,
                        "word_count": self.count_words(),
                        "word_frequency": self.word_frequency(),
                        "language": self.detect_language(),
                        "summary": self.summarize(),
                        "sentiment": self.sentiment_analysis(),
                        "named_entities": self.named_entity_recognition(),
                        "keywords": self.extract_keywords(),
                        "lemmatized_words": self.lemmatize(),
                        "sentence_lengths": self.sentence_length_analysis()
                    }
                    results.append(result)
                return json.dumps(results, ensure_ascii=False, indent=4)

            def topic_analysis(self, topics, texts):
                """تحلیل موضوعی متن."""
                topic_keywords = {topic: re.compile('|'.join(keywords)) for topic, keywords in topics.items()}
                
                result = {}
                for text in texts:
                    cleaned_text = re.sub(r'[^\w\s]', '', text)
                    for topic, pattern in topic_keywords.items():
                        if pattern.search(cleaned_text):
                            result[topic] = text
                            break
                    else:
                        result["others"] = text
                return json.dumps(result, ensure_ascii=False, indent=4)

            def extract_main_topic(self):
                """استخراج موضوع اصلی هر پاراگراف یا جمله."""
                # تقسیم متن به پاراگراف‌ها
                paragraphs = self.text.split('\n')
                result = {}
                
                for i, paragraph in enumerate(paragraphs):
                    # پاکسازی و توکن‌سازی پاراگراف
                    cleaned_paragraph = re.sub(r'[^\w\s]', '', paragraph)
                    tokens = nltk.word_tokenize(cleaned_paragraph)
                    word_count = Counter(tokens)
                    
                    # پیدا کردن پرتکرارترین کلمه
                    if word_count:
                        most_common_word, _ = word_count.most_common(1)[0]
                        result[f"paragraph_{i + 1}"] = {
                            "topic": most_common_word,
                            "content": paragraph.strip()
                        }
                
                return json.dumps(result, ensure_ascii=False, indent=4)
















        class MachineLearning:
            def __init__(self, model):
                self.model = model
                self.scaler = StandardScaler()
                self.X_train = None
                self.X_test = None
                self.y_train = None
                self.y_test = None

            def preprocess_data(self, X, y, test_size=0.2, random_state=42):
                """
                داده‌ها را به مجموعه آموزش و آزمون تقسیم می‌کند و مقیاس‌گذاری را انجام می‌دهد.
                """
                self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
                self.X_train = self.scaler.fit_transform(self.X_train)
                self.X_test = self.scaler.transform(self.X_test)

            def train_model(self):
                """
                مدل را با داده‌های آموزشی آموزش می‌دهد.
                """
                self.model.fit(self.X_train, self.y_train)

            def evaluate_model(self):
                """
                مدل را با داده‌های آزمون ارزیابی می‌کند و دقت و ماتریس سردرگمی را نمایش می‌دهد.
                """
                y_pred = self.model.predict(self.X_test)
                accuracy = accuracy_score(self.y_test, y_pred)
                conf_matrix = confusion_matrix(self.y_test, y_pred)
                
                print(f"Accuracy: {accuracy:.2f}")
                print("Confusion Matrix:")
                print(conf_matrix)
                print("\nClassification Report:")
                print(classification_report(self.y_test, y_pred))

                self.plot_confusion_matrix(conf_matrix)

            def plot_confusion_matrix(self, conf_matrix):
                """
                ماتریس سردرگمی را رسم می‌کند.
                """
                plt.figure(figsize=(8, 6))
                plt.imshow(conf_matrix, interpolation='nearest', cmap=plt.cm.Blues)
                plt.title('Confusion Matrix')
                plt.colorbar()
                tick_marks = np.arange(len(np.unique(self.y_test)))
                plt.xticks(tick_marks, np.unique(self.y_test))
                plt.yticks(tick_marks, np.unique(self.y_test))
                plt.ylabel('True label')
                plt.xlabel('Predicted label')
                plt.show()

            def predict(self, X_new):
                """
                پیش‌بینی بر اساس مدل آموزش‌دیده شده انجام می‌دهد.
                """
                X_new_scaled = self.scaler.transform(X_new)
                return self.model.predict(X_new_scaled)

            def save_model(self, filename):
                """
                مدل آموزش‌دیده شده را ذخیره می‌کند.
                """
                joblib.dump(self.model, filename)

            def load_model(self, filename):
                """
                مدل را از یک فایل بارگذاری می‌کند.
                """
                self.model = joblib.load(filename)

            def hyperparameter_tuning(self, param_grid, cv=5):
                """
                جستجوی هایپرپارامترها را انجام می‌دهد.
                """
                grid_search = GridSearchCV(self.model, param_grid, cv=cv)
                grid_search.fit(self.X_train, self.y_train)
                self.model = grid_search.best_estimator_
                print(f"Best parameters: {grid_search.best_params_}")















        class DeepLearningModel:
            

            def __init__(self, input_shape, num_classes):
                self.input_shape = input_shape
                self.num_classes = num_classes
                self.model = None
                self.history = None

            def prepare_data(self, X, y, test_size=0.2, random_state=42):
                """آماده‌سازی داده‌ها: تقسیم داده‌ها به مجموعه‌های آموزشی و آزمون"""
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
                return X_train, X_test, y_train, y_test

            def preprocess_data(self, X):
                """پیش‌پردازش داده‌ها: استانداردسازی یا نرمال‌سازی داده‌ها"""
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                return X_scaled

            def build_model(self, layers_config):
                """ساخت مدل: تعریف ساختار مدل شبکه عصبی"""
                self.model = keras.Sequential()
                for units, activation in layers_config:
                    self.model.add(keras.layers.Dense(units, activation=activation, input_shape=self.input_shape))
                    self.model.add(keras.layers.Dropout(0.5))
                
                self.model.add(keras.layers.Dense(self.num_classes, activation='softmax'))

                self.model.compile(optimizer='adam',
                                loss='sparse_categorical_crossentropy',
                                metrics=['accuracy'])

            def train_model(self, X_train, y_train, epochs=10, batch_size=32):
                """آموزش مدل: آموزش شبکه عصبی با استفاده از داده‌های آموزشی"""
                early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
                model_checkpoint = ModelCheckpoint('best_model.h5', save_best_only=True)

                self.history = self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, 
                                            validation_split=0.2, callbacks=[early_stopping, model_checkpoint])

            def evaluate_model(self, X_test, y_test):
                """ارزیابی مدل: ارزیابی عملکرد مدل بر روی داده‌های آزمون"""
                test_loss, test_accuracy = self.model.evaluate(X_test, y_test)
                print(f"Test Loss: {test_loss}, Test Accuracy: {test_accuracy}")

            def predict(self, X):
                """پیش‌بینی: استفاده از مدل برای پیش‌بینی بر روی داده‌های جدید"""
                return self.model.predict(X)

            def load_model(self, filepath):
                """بارگذاری مدل از فایل"""
                self.model = keras.models.load_model(filepath)





        class Computer_Vision:
            def __init__(self, image_path):
                self.image_path = image_path
                self.image = self.load_image()
                self.processed_image = None

            def load_image(self):
                """Load image from the specified path"""
                image = cv2.imread(self.image_path)
                if image is None:
                    raise ValueError("Unable to load image. Check the image path.")
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            def show_image(self, title="Image"):
                """Display the image using matplotlib"""
                plt.imshow(self.image)
                plt.title(title)
                plt.axis('off')
                plt.show()

            def preprocess_image(self, resize_dim=(256, 256), grayscale=False):
                """Preprocess the image: resize and convert to grayscale"""
                image = cv2.resize(self.image, resize_dim)
                if grayscale:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                self.processed_image = image

            def detect_edges(self):
                """Detect edges using Canny method"""
                if self.processed_image is None:
                    raise ValueError("Processed image is not available. Please preprocess the image first.")
                edges = cv2.Canny(self.processed_image, 100, 200)
                return edges

            def apply_gaussian_blur(self, kernel_size=(5, 5)):
                """Apply Gaussian Blur to the processed image"""
                if self.processed_image is None:
                    raise ValueError("Processed image is not available. Please preprocess the image first.")
                self.processed_image = cv2.GaussianBlur(self.processed_image, kernel_size, 0)

            def detect_features(self, method='ORB'):
                """Detect features in the image using specified method (ORB or SIFT)"""
                if self.processed_image is None:
                    raise ValueError("Processed image is not available. Please preprocess the image first.")

                if method == 'ORB':
                    orb = cv2.ORB_create()
                    keypoints, descriptors = orb.detectAndCompute(self.processed_image, None)
                    output_image = cv2.drawKeypoints(self.processed_image, keypoints, None, color=(0, 255, 0))
                    self.processed_image = output_image
                elif method == 'SIFT':
                    sift = cv2.SIFT_create()
                    keypoints, descriptors = sift.detectAndCompute(self.processed_image, None)
                    output_image = cv2.drawKeypoints(self.processed_image, keypoints, None, color=(0, 255, 0))
                    self.processed_image = output_image
                else:
                    raise ValueError("Unsupported method. Choose 'ORB' or 'SIFT'.")

            def rotate_image(self, angle):
                """Rotate the processed image by a given angle"""
                if self.processed_image is None:
                    raise ValueError("Processed image is not available. Please preprocess the image first.")
                h, w = self.processed_image.shape[:2]
                center = (w // 2, h // 2)
                matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                self.processed_image = cv2.warpAffine(self.processed_image, matrix, (w, h))

            def show_processed_image(self, title="Processed Image"):
                """Display the processed image"""
                if self.processed_image is None:
                    raise ValueError("Processed image is not available. Please preprocess the image first.")
                plt.imshow(self.processed_image, cmap='gray' if len(self.processed_image.shape) == 2 else None)
                plt.title(title)
                plt.axis('off')
                plt.show()

            def save_image(self, save_path):
                """Save the processed image"""
                if self.processed_image is None:
                    raise ValueError("Processed image is not available. Please preprocess the image first.")
                cv2.imwrite(save_path, cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR))





        class Robotics:
            def __init__(self, name, serial_port='/dev/ttyUSB0', baud_rate=9600):
                self.name = name
                self.position = (0, 0)
                self.orientation = 0  # زاویه در درجه
                self.battery_level = 100  # درصد
                self.history = []  # تاریخچه حرکات
                self.state = "idle"  # حالت ربات
                self.serial_port = serial.Serial(serial_port, baud_rate)  # ارتباط سریال با آردوینو

            def move_forward(self, distance):
                if self.battery_level <= 0:
                    print("Battery is empty. Please charge the robot.")
                    return
                
                # محاسبه موقعیت جدید ربات بعد از حرکت به جلو
                x, y = self.position
                x += distance * cos(radians(self.orientation))
                y += distance * sin(radians(self.orientation))
                self.position = (x, y)
                self.battery_level -= distance * 0.1  # کاهش سطح باتری
                self.history.append(('move_forward', distance))  # ذخیره تاریخچه حرکت
                self.send_to_arduino(f'MOVE_FORWARD,{distance}')

            def move_backward(self, distance):
                if self.battery_level <= 0:
                    print("Battery is empty. Please charge the robot.")
                    return
                
                # محاسبه موقعیت جدید ربات بعد از حرکت به عقب
                x, y = self.position
                x -= distance * cos(radians(self.orientation))
                y -= distance * sin(radians(self.orientation))
                self.position = (x, y)
                self.battery_level -= distance * 0.1  # کاهش سطح باتری
                self.history.append(('move_backward', distance))  # ذخیره تاریخچه حرکت
                self.send_to_arduino(f'MOVE_BACKWARD,{distance}')

            def turn(self, angle):
                self.orientation = (self.orientation + angle) % 360
                self.history.append(('turn', angle))  # ذخیره تاریخچه چرخش
                self.send_to_arduino(f'TURN,{angle}')

            def move_to(self, target_position):
                if self.battery_level <= 0:
                    print("Battery is empty. Please charge the robot.")
                    return
                
                # محاسبه فاصله و زاویه به سمت موقعیت هدف
                target_x, target_y = target_position
                x, y = self.position
                distance = sqrt((target_x - x)**2 + (target_y - y)**2)
                angle_to_turn = (degrees(atan2(target_y - y, target_x - x)) - self.orientation) % 360
                
                if distance > 0:
                    self.turn(angle_to_turn)
                    self.move_forward(distance)
                    self.history.append(('move_to', target_position))  # ذخیره تاریخچه حرکت به موقعیت
                    self.send_to_arduino(f'MOVE_TO,{target_position}')

            def charge_battery(self, amount):
                self.battery_level = min(100, self.battery_level + amount)
                self.send_to_arduino(f'CHARGE_BATTERY,{amount}')

            def send_to_arduino(self, message):
                """ارسال پیام به آردوینو"""
                if self.serial_port.is_open:
                    self.serial_port.write(message.encode())
                else:
                    print("Serial port is not open.")

            def get_position(self):
                return self.position

            def get_orientation(self):
                return self.orientation

            def get_battery_level(self):
                return self.battery_level

            def get_history(self):
                return self.history

            def display_status(self):
                print(f"Robot Name: {self.name}")
                print(f"Position: {self.position}")
                print(f"Orientation: {self.orientation} degrees")
                print(f"Battery Level: {self.battery_level}%")
                print(f"State: {self.state}")
                print(f"Movement History: {self.history}")

            def set_state(self, state):
                self.state = state




        class ExpertSystems:
            def __init__(self, filename):
                self.data = self.load_data(filename)

            def load_data(self, filename):
                with open(filename, 'r') as file:
                    return json.load(file)

            def ModelAnswer(self, topic):
                for item in self.data:
                    if item['topic'].lower() == topic.lower() or item['topic'].lower() in topic.lower():
                        return item['content']
                return "Sorry, I don't have information on that topic."























    class Models:

        class RandomForest:
            def init(self, n_trees=100, max_depth=None, min_samples_split=2):
                self.n_trees = n_trees
                self.max_depth = max_depth
                self.min_samples_split = min_samples_split
                self.trees = []

            def _bootstrap(self, X, y):
                n_samples = X.shape[0]
                indices = np.random.choice(range(n_samples), size=n_samples, replace=True)
                return X[indices], y[indices]

            def _fit_tree(self, X, y):
                tree = DecisionTreeClassifier(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
                tree.fit(X, y)
                return tree

            def fit(self, X, y):
                for _ in range(self.n_trees):
                    X_bootstrap, y_bootstrap = self._bootstrap(X, y)
                    tree = self._fit_tree(X_bootstrap, y_bootstrap)
                    self.trees.append(tree)

            def _predict_tree(self, tree, X):
                return tree.predict(X)

            def predict(self, X):
                predictions = np.array([self._predict_tree(tree, X) for tree in self.trees])
                return np.array([np.bincount(pred).argmax() for pred in predictions.T])

            def score(self, X, y):
                predictions = self.predict(X)
                return accuracy_score(y, predictions)








        

        class XLNetModel:
            def init(self):
                self.tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased')
                self.model = XLNetForSequenceClassification.from_pretrained('xlnet-base-cased')

            def generate_text(self, prompt):
                input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
                with torch.no_grad():
                    outputs = self.model(input_ids)
                return outputs

            def save_model(self, save_directory):
                self.model.save_pretrained(save_directory)
                self.tokenizer.save_pretrained(save_directory)

            def load_model(self, load_directory):
                try:
                    self.tokenizer = XLNetTokenizer.from_pretrained(load_directory)
                    self.model = XLNetForSequenceClassification.from_pretrained(load_directory)
                    self.model.eval()
                except Exception as e:
                    print(f"Error loading model from {load_directory}: {e}")











        

        class RoBERTaModel:
            def init(self):
                self.tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
                self.model = RobertaForSequenceClassification.from_pretrained('roberta-base')

            def generate_text(self, prompt):
                input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
                with torch.no_grad():
                    outputs = self.model(input_ids)
                return outputs

            def save_model(self, save_directory):
                self.model.save_pretrained(save_directory)
                self.tokenizer.save_pretrained(save_directory)

            def load_model(self, load_directory):
                try:
                    self.tokenizer = RobertaTokenizer.from_pretrained(load_directory)
                    self.model = RobertaForSequenceClassification.from_pretrained(load_directory)
                    self.model.eval()
                except Exception as e:
                    print(f"Error loading model from {load_directory}: {e}")










        class T5Model:
            def init(self):
                self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
                self.model = T5ForConditionalGeneration.from_pretrained('t5-small')

            def generate_text(self, prompt, max_length=100):
                input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
                with torch.no_grad():
                    output = self.model.generate(input_ids, max_length=max_length)
                return self.tokenizer.decode(output[0], skip_special_tokens=True)

            def save_model(self, save_directory):
                self.model.save_pretrained(save_directory)
                self.tokenizer.save_pretrained(save_directory)

            def load_model(self, load_directory):
                try:
                    self.tokenizer = T5Tokenizer.from_pretrained(load_directory)
                    self.model = T5ForConditionalGeneration.from_pretrained(load_directory)
                    self.model.eval()
                except Exception as e:
                    print(f"Error loading model from {load_directory}: {e}")
















        

        class BERT:


            class BERT_Model:

                def generate_text(user_input, model_name="microsoft/DialoGPT-medium", max_length=1000, chat_history=None, train_data=None):
                    # Load the pre-trained model and tokenizer
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    model = AutoModelForCausalLM.from_pretrained(model_name)

                    # Fine-tune the model if training data is provided
                    if train_data:
                        print("Training the model...")
                        optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)
                        for epoch in range(3):  # You can customize the number of epochs
                            for input_text, response_text in train_data:
                                inputs = tokenizer(input_text + tokenizer.eos_token, return_tensors="pt")
                                labels = tokenizer(response_text + tokenizer.eos_token, return_tensors="pt")["input_ids"]
                                outputs = model(**inputs, labels=labels)
                                loss = outputs.loss
                                loss.backward()
                                optimizer.step()
                                optimizer.zero_grad()
                            print(f"Epoch {epoch + 1} completed.")

                    # Encode user input and append to chat history
                    new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors="pt")

                    # Concatenate new user input with chat history (if exists)
                    chat_history = torch.cat([chat_history, new_input_ids], dim=-1) if chat_history is not None else new_input_ids

                    # Generate a response
                    response_ids = model.generate(chat_history, max_length=max_length, pad_token_id=tokenizer.eos_token_id)

                    # Decode and return the response
                    response = tokenizer.decode(response_ids[:, chat_history.shape[-1]:][0], skip_special_tokens=True)
                    return response, chat_history







            class TrainedModel:
                def generate_text(user_input,chat_history_ids=None):
                    # Load the pre-trained DialoGPT model and tokenizer
                    model_name = "microsoft/DialoGPT-medium"
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    model = AutoModelForCausalLM.from_pretrained(model_name)

                    new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors="pt")

                    chat_history_ids = torch.cat([chat_history_ids, new_input_ids], dim=-1) if chat_history_ids is not None else new_input_ids

                    # Generate a response
                    response_ids = model.generate(chat_history_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

                     # Decode and print the response
                    return(tokenizer.decode(response_ids[:, chat_history_ids.shape[-1]:][0], skip_special_tokens=True))











        class GPT:


            class GPT_Model:
                def __init__(self, model_name='gpt2', max_length=512):
                    # بارگذاری مدل و توکنایزر
                    self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
                    self.model = GPT2LMHeadModel.from_pretrained(model_name)
                    self.max_length = max_length

                def preprocess_text(self, text):
                    """متن را پیش‌پردازش می‌کند."""
                    # تبدیل به حروف کوچک
                    text = text.lower()
                    # حذف کاراکترهای غیرضروری
                    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
                    return text

                def prepare_dataset(self, texts):
                    """داده‌ها را برای آموزش آماده می‌کند."""
                    processed_texts = [self.preprocess_text(text) for text in texts]
                    inputs = self.tokenizer(processed_texts, return_tensors='pt', max_length=self.max_length, truncation=True, padding=True)
                    return inputs['input_ids']

                def train(self, texts, output_dir='./results', num_train_epochs=3, per_device_train_batch_size=2):
                    """مدل را با داده‌های ورودی آموزش می‌دهد."""
                    input_ids = self.prepare_dataset(texts)

                    # تبدیل به TensorDataset
                    dataset = TensorDataset(input_ids)

                    # تنظیمات آموزش
                    training_args = TrainingArguments(
                        output_dir=output_dir,
                        num_train_epochs=num_train_epochs,
                        per_device_train_batch_size=per_device_train_batch_size,
                        save_steps=10_000,
                        save_total_limit=2,
                        logging_dir='./logs',
                        logging_steps=200,
                    )

                    trainer = Trainer(
                        model=self.model,
                        args=training_args,
                        train_dataset=dataset,
                    )

                    # آموزش مدل
                    trainer.train()

                def generate_response(self, input_text, max_length=100):
                    """پاسخ را با توجه به ورودی تولید می‌کند."""
                    input_ids = self.tokenizer.encode(input_text, return_tensors='pt')
                    if torch.cuda.is_available():
                        input_ids = input_ids.to('cuda')
                        self.model.to('cuda')

                    output = self.model.generate(input_ids, max_length=max_length, num_return_sequences=1)
                    response = self.tokenizer.decode(output[0], skip_special_tokens=True)
                    return response


            



            class TrainedModel:

                def generate_text(prompt, max_length=100, num_beams=5, temperature=1.0, top_k=50, top_p=0.95):
                    # Initialize tokenizer and models
                    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                    
                    bert_tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
                    bert_model = DistilBertModel.from_pretrained("distilbert-base-uncased").to(device)
                    gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
                    gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2").to(device)

                    # Tokenize the prompt with DistilBERT
                    inputs = bert_tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True).to(device)
                    
                    # Get the hidden states from DistilBERT
                    with torch.no_grad():
                        outputs = bert_model(**inputs)
                    
                    # Use the [CLS] token's hidden state
                    cls_hidden_state = outputs.last_hidden_state[:, 0, :].unsqueeze(0)  # Taking the [CLS] token's hidden state
                    
                    # Generate initial input for GPT-2 (need to convert hidden state to input_ids)
                    gpt2_input_ids = gpt2_tokenizer.encode(prompt, return_tensors='pt').to(device)
                    
                    # Generate text using GPT-2
                    gpt2_outputs = gpt2_model.generate(input_ids=gpt2_input_ids,
                                                    max_length=max_length,
                                                    num_beams=num_beams,
                                                    temperature=temperature,
                                                    top_k=top_k,
                                                    top_p=top_p,
                                                    no_repeat_ngram_size=2,
                                                    early_stopping=True)

                    # Decode the output from GPT-2
                    generated_text = gpt2_tokenizer.decode(gpt2_outputs[0], skip_special_tokens=True)
                    
                    return generated_text








































    

    class Algorithms:






        class SupervisedLearning:


            class Classifier:
                def __init__(self, model='RandomForest'):
                    if model == 'RandomForest':
                        self.model = RandomForestClassifier()
                    elif model == 'SVM':
                        self.model = SVC()
                    else:
                        raise ValueError("Model not supported. Choose 'RandomForest' or 'SVM'.")

                def train(self, X, y, test_size=0.2, random_state=42):
                    """Train the model on the provided dataset."""
                    self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
                    self.model.fit(self.X_train, self.y_train)
                    print("Model trained successfully.")

                def predict(self, X):
                    """Make predictions on the provided dataset."""
                    return self.model.predict(X)

                def evaluate(self):
                    """Evaluate the model using accuracy and other metrics."""
                    y_pred = self.predict(self.X_test)
                    accuracy = accuracy_score(self.y_test, y_pred)
                    report = classification_report(self.y_test, y_pred)
                    conf_matrix = confusion_matrix(self.y_test, y_pred)
                    return {
                        "Accuracy":f"{accuracy:.2f}",
                        "Classification Report":report,
                        "Confusion Matrix":conf_matrix
                    }
            





            class Regression:

                class DecisionTree:
                    def __init__(self, max_depth=None):
                        self.max_depth = max_depth
                        self.tree = None

                    def fit(self, X, y):
                        self.tree = self._build_tree(X, y)

                    def _build_tree(self, X, y, depth=0):
                        num_samples, num_features = X.shape
                        unique_classes = np.unique(y)

                        # Stop criteria
                        if (len(unique_classes) == 1) or (self.max_depth and depth >= self.max_depth):
                            return unique_classes[0]

                        # Find the best split
                        best_feature, best_threshold = self._best_split(X, y)
                        left_indices = X[:, best_feature] < best_threshold
                        right_indices = X[:, best_feature] >= best_threshold

                        left_tree = self._build_tree(X[left_indices], y[left_indices], depth + 1)
                        right_tree = self._build_tree(X[right_indices], y[right_indices], depth + 1)

                        return (best_feature, best_threshold, left_tree, right_tree)

                    def _best_split(self, X, y):
                        num_samples, num_features = X.shape
                        best_gini = float('inf')
                        best_feature = None
                        best_threshold = None

                        for feature in range(num_features):
                            thresholds = np.unique(X[:, feature])
                            for threshold in thresholds:
                                gini = self._calculate_gini(X, y, feature, threshold)
                                if gini < best_gini:
                                    best_gini = gini
                                    best_feature = feature
                                    best_threshold = threshold

                        return best_feature, best_threshold

                    def _calculate_gini(self, X, y, feature, threshold):
                        left_indices = X[:, feature] < threshold
                        right_indices = X[:, feature] >= threshold

                        left_labels = y[left_indices]
                        right_labels = y[right_indices]

                        gini_left = self._gini_index(left_labels)
                        gini_right = self._gini_index(right_labels)

                        # Weighted average Gini impurity
                        gini = (len(left_labels) * gini_left + len(right_labels) * gini_right) / len(y)
                        return gini

                    def _gini_index(self, y):
                        if len(y) == 0:
                            return 0
                        classes, counts = np.unique(y, return_counts=True)
                        probabilities = counts / len(y)
                        gini = 1 - np.sum(probabilities ** 2)
                        return gini

                    def predict(self, X):
                        return np.array([self._predict_sample(x, self.tree) for x in X])

                    def _predict_sample(self, x, tree):
                        if isinstance(tree, tuple):
                            feature, threshold, left_tree, right_tree = tree
                            if x[feature] < threshold:
                                return self._predict_sample(x, left_tree)
                            else:
                                return self._predict_sample(x, right_tree)
                        else:
                            return tree

                    def score(self, X, y):
                        predictions = self.predict(X)
                        return np.mean(predictions == y)
                



                

                class SupportVectorMachine:
                    def __init__(self, kernel='linear', C=1.0):
                        """
                        Initializes the SVM model with the given kernel and C parameter.
                        
                        :param kernel: Type of kernel to be used ('linear', 'poly', 'rbf', etc.)
                        :param C: Regularization parameter
                        """
                        self.kernel = kernel
                        self.C = C
                        self.model = SVC(kernel=self.kernel, C=self.C)

                    def fit(self, X, y):
                        """
                        Trains the SVM model using the provided features and labels.
                        
                        :param X: Feature matrix
                        :param y: Corresponding labels
                        """
                        self.model.fit(X, y)

                    def predict(self, X):
                        """
                        Predicts the labels for the given features.
                        
                        :param X: Feature matrix for prediction
                        :return: Predicted labels
                        """
                        return self.model.predict(X)

                    def score(self, X, y):
                        """
                        Evaluates the model's accuracy on the provided test data.
                        
                        :param X: Feature matrix
                        :param y: Corresponding true labels
                        :return: Accuracy score
                        """
                        predictions = self.predict(X)
                        return accuracy_score(y, predictions)








            

            class NaiveBayes:
                def __init__(self):
                    self.class_priors = {}
                    self.feature_likelihoods = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
                    self.class_counts = defaultdict(int)
                    self.num_features = 0

                def fit(self, X, y):
                    """ آموزش مدل با داده‌های ورودی و برچسب‌ها """
                    self.num_features = X.shape[1]
                    total_samples = len(y)
                    
                    for i in range(total_samples):
                        label = y[i]
                        self.class_counts[label] += 1
                        
                        for j in range(self.num_features):
                            feature_value = X[i][j]
                            self.feature_likelihoods[label][j][feature_value] += 1
                    
                    # محاسبه احتمال‌های پیشین برای هر کلاس
                    for label, count in self.class_counts.items():
                        self.class_priors[label] = count / total_samples
                        
                    # محاسبه احتمال‌های شرطی برای ویژگی‌ها
                    for label in self.feature_likelihoods:
                        for feature_index in self.feature_likelihoods[label]:
                            total_count = sum(self.feature_likelihoods[label][feature_index].values())
                            for feature_value in self.feature_likelihoods[label][feature_index]:
                                self.feature_likelihoods[label][feature_index][feature_value] /= total_count

                def predict(self, X):
                    """ پیش‌بینی کلاس برای داده‌های ورودی """
                    predictions = []
                    for sample in X:
                        class_scores = {}
                        for label in self.class_priors:
                            # محاسبه احتمال برای هر کلاس
                            score = np.log(self.class_priors[label])  # احتمال پیشین
                            for j in range(self.num_features):
                                feature_value = sample[j]
                                likelihood = self.feature_likelihoods[label][j].get(feature_value, 0)
                                score += np.log(likelihood + 1e-9)  # جلوگیری از صفر در لگاریتم
                            class_scores[label] = score
                        
                        # انتخاب کلاس با بیشترین نمره
                        predicted_class = max(class_scores, key=class_scores.get)
                        predictions.append(predicted_class)
                    
                    return np.array(predictions)







            class LogisticRegression:
                def __init__(self, learning_rate=0.01, num_iterations=1000):
                    self.learning_rate = learning_rate
                    self.num_iterations = num_iterations
                    self.weights = None
                    self.bias = None

                def sigmoid(self, z):
                    return 1 / (1 + np.exp(-z))

                def fit(self, X, y):
                    num_samples, num_features = X.shape
                    self.weights = np.zeros(num_features)
                    self.bias = 0

                    for _ in range(self.num_iterations):
                        linear_model = np.dot(X, self.weights) + self.bias
                        y_predicted = self.sigmoid(linear_model)

                        # Gradient descent
                        dw = (1 / num_samples) * np.dot(X.T, (y_predicted - y))
                        db = (1 / num_samples) * np.sum(y_predicted - y)

                        self.weights -= self.learning_rate * dw
                        self.bias -= self.learning_rate * db

                def predict(self, X):
                    linear_model = np.dot(X, self.weights) + self.bias
                    y_predicted = self.sigmoid(linear_model)
                    y_predicted_class = [1 if i > 0.5 else 0 for i in y_predicted]
                    return np.array(y_predicted_class)

                def accuracy(self, y_true, y_pred):
                    return np.sum(y_true == y_pred) / len(y_true)






            class LinearRegression:
                def __init__(self):
                    self.coefficients = None
                    self.intercept = None

                def fit(self, X, y):
                    """
                    آموزش مدل با استفاده از داده‌های ورودی X و مقادیر هدف y
                    """
                    X = np.array(X)
                    y = np.array(y)
                    
                    # اضافه کردن یک ستون از 1 ها برای محاسبه مقطع
                    X_b = np.c_[np.ones((X.shape[0], 1)), X]  # اضافه کردن x0 = 1 برای هر نمونه

                    # محاسبه ضرایب با استفاده از فرمول (X^T * X)^-1 * X^T * y
                    theta_best = np.linalg.inv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)
                    
                    self.intercept = theta_best[0]
                    self.coefficients = theta_best[1:]

                def predict(self, X):
                    """
                    پیش‌بینی مقادیر با استفاده از مدل آموزش دیده
                    """
                    X = np.array(X)
                    return self.intercept + X.dot(self.coefficients)

                def mean_squared_error(self, y_true, y_pred):
                    """
                    محاسبه خطای میانگین مربعات (MSE)
                    """
                    return np.mean((y_true - y_pred) ** 2)

                def score(self, X, y):
                    """
                    محاسبه ضریب تعیین (R^2)
                    """
                    y_pred = self.predict(X)
                    total_variance = np.var(y)
                    residual_variance = np.var(y - y_pred)
                    return 1 - (residual_variance / total_variance)
























        class UnsupervisedLearning:







            class KMeans:
                def __init__(self, n_clusters=3, max_iter=300, tol=1e-4):
                    self.n_clusters = n_clusters
                    self.max_iter = max_iter
                    self.tol = tol
                    self.centroids = None
                    self.labels = None

                def fit(self, X):
                    # انتخاب تصادفی مراکز اولیه
                    random_indices = np.random.choice(X.shape[0], self.n_clusters, replace=False)
                    self.centroids = X[random_indices]

                    for _ in range(self.max_iter):
                        # مرحله 1: محاسبه برچسب ها
                        self.labels = self._assign_labels(X)

                        # مرحله 2: به روز رسانی مراکز
                        new_centroids = self._update_centroids(X)

                        # بررسی همگرایی
                        if np.linalg.norm(new_centroids - self.centroids) < self.tol:
                            break

                        self.centroids = new_centroids

                def _assign_labels(self, X):
                    distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
                    return np.argmin(distances, axis=1)

                def _update_centroids(self, X):
                    return np.array([X[self.labels == i].mean(axis=0) for i in range(self.n_clusters)])

                def predict(self, X):
                    return self._assign_labels(X)

                def plot(self, X):
                    plt.scatter(X[:, 0], X[:, 1], c=self.labels, cmap='viridis')
                    plt.scatter(self.centroids[:, 0], self.centroids[:, 1], s=300, c='red', marker='X')
                    plt.title('K-Means Clustering')
                    plt.xlabel('Feature 1')
                    plt.ylabel('Feature 2')
                    plt.show()






            class GaussianMixture:
                def __init__(self, n_components, max_iter=100, tol=1e-3):
                    self.n_components = n_components
                    self.max_iter = max_iter
                    self.tol = tol
                    self.means = None
                    self.covariances = None
                    self.weights = None
                    self.log_likelihood = None

                def _initialize_parameters(self, X):
                    n_samples, n_features = X.shape
                    self.weights = np.ones(self.n_components) / self.n_components
                    self.means = X[np.random.choice(n_samples, self.n_components, False)]
                    self.covariances = np.array([np.eye(n_features)] * self.n_components)

                def _e_step(self, X):
                    responsibilities = np.zeros((X.shape[0], self.n_components))
                    for k in range(self.n_components):
                        responsibilities[:, k] = self.weights[k] * multivariate_normal.pdf(X, mean=self.means[k], cov=self.covariances[k])
                    responsibilities /= responsibilities.sum(axis=1, keepdims=True)
                    return responsibilities

                def _m_step(self, X, responsibilities):
                    n_samples = X.shape[0]
                    for k in range(self.n_components):
                        N_k = responsibilities[:, k].sum()
                        self.weights[k] = N_k / n_samples
                        self.means[k] = (responsibilities[:, k] @ X) / N_k
                        diff = X - self.means[k]
                        self.covariances[k] = (responsibilities[:, k] * diff).T @ diff / N_k

                def fit(self, X):
                    self._initialize_parameters(X)
                    for i in range(self.max_iter):
                        responsibilities = self._e_step(X)
                        self._m_step(X, responsibilities)
                        log_likelihood_new = np.sum(np.log(responsibilities.sum(axis=1)))
                        if self.log_likelihood is not None and abs(log_likelihood_new - self.log_likelihood) < self.tol:
                            break
                        self.log_likelihood = log_likelihood_new

                def predict(self, X):
                    responsibilities = self._e_step(X)
                    return np.argmax(responsibilities, axis=1)

                def score(self, X):
                    responsibilities = self._e_step(X)
                    return np.sum(np.log(responsibilities.sum(axis=1)))











            class PCA:
                def __init__(self, n_components=None):
                    self.n_components = n_components
                    self.mean = None
                    self.components = None
                    self.explained_variance = None

                def fit(self, X):
                    # محاسبه میانگین
                    self.mean = np.mean(X, axis=0)
                    # مرکز زدایی داده‌ها
                    X_centered = X - self.mean
                    # محاسبه ماتریس کوواریانس
                    covariance_matrix = np.cov(X_centered, rowvar=False)
                    # محاسبه مقادیر ویژه و بردارهای ویژه
                    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
                    # مرتب کردن مقادیر ویژه و بردارها
                    sorted_indices = np.argsort(eigenvalues)[::-1]
                    eigenvalues = eigenvalues[sorted_indices]
                    eigenvectors = eigenvectors[:, sorted_indices]
                    
                    # انتخاب تعداد مشخصی از مولفه‌ها
                    if self.n_components is not None:
                        eigenvectors = eigenvectors[:, :self.n_components]
                        eigenvalues = eigenvalues[:self.n_components]

                    self.components = eigenvectors
                    self.explained_variance = eigenvalues

                def transform(self, X):
                    # مرکز زدایی داده‌ها
                    X_centered = X - self.mean
                    # تبدیل داده‌ها به فضای جدید
                    return np.dot(X_centered, self.components)

                def fit_transform(self, X):
                    self.fit(X)
                    return self.transform(X)

                def inverse_transform(self, X_transformed):
                    # تبدیل مجدد به فضای اصلی
                    return np.dot(X_transformed, self.components.T) + self.mean

                def explained_variance_ratio(self):
                    # محاسبه نسبت واریانس توضیح داده شده
                    return self.explained_variance / np.sum(self.explained_variance)
                







            class SVD:
                def __init__(self, matrix):
                    self.matrix = matrix
                    self.U = None
                    self.S = None
                    self.VT = None

                def compute_svd(self):
                    """محاسبه SVD برای ماتریس ورودی."""
                    self.U, s, self.VT = np.linalg.svd(self.matrix, full_matrices=False)
                    self.S = np.diag(s)

                def reconstruct_matrix(self):
                    """بازسازی ماتریس اولیه از U، S و VT."""
                    if self.U is None or self.S is None or self.VT is None:
                        raise ValueError("SVD باید ابتدا محاسبه شود.")
                    return np.dot(self.U, np.dot(self.S, self.VT))

                def get_singular_values(self):
                    """دریافت مقادیر منفرد."""
                    if self.S is None:
                        raise ValueError("SVD باید ابتدا محاسبه شود.")
                    return np.diagonal(self.S)

                def get_left_singular_vectors(self):
                    """دریافت وکتورهای منفرد چپ."""
                    if self.U is None:
                        raise ValueError("SVD باید ابتدا محاسبه شود.")
                    return self.U

                def get_right_singular_vectors(self):
                    """دریافت وکتورهای منفرد راست."""
                    if self.VT is None:
                        raise ValueError("SVD باید ابتدا محاسبه شود.")
                    return self.VT









            class Autoencoder:
                def __init__(self, input_shape, encoding_dim):
                    self.input_shape = input_shape
                    self.encoding_dim = encoding_dim
                    self.autoencoder = None
                    self.encoder = None
                    self.decoder = None
                    self.build_model()

                def build_model(self):
                    # Encoder
                    input_img = layers.Input(shape=self.input_shape)
                    encoded = layers.Flatten()(input_img)
                    encoded = layers.Dense(self.encoding_dim, activation='relu')(encoded)

                    # Decoder
                    decoded = layers.Dense(np.prod(self.input_shape), activation='sigmoid')(encoded)
                    decoded = layers.Reshape(self.input_shape)(decoded)

                    # Autoencoder
                    self.autoencoder = models.Model(input_img, decoded)
                    self.encoder = models.Model(input_img, encoded)

                    # Create decoder model
                    encoded_input = layers.Input(shape=(self.encoding_dim,))
                    decoder_layer = self.autoencoder.layers[-1]
                    self.decoder = models.Model(encoded_input, decoder_layer(encoded_input))

                    self.autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

                def train(self, x_train, x_val, epochs=50, batch_size=256):
                    self.autoencoder.fit(x_train, x_train,
                                        epochs=epochs,
                                        batch_size=batch_size,
                                        shuffle=True,
                                        validation_data=(x_val, x_val))

                def encode(self, data):
                    return self.encoder.predict(data)

                def decode(self, encoded_data):
                    return self.decoder.predict(encoded_data)

                def reconstruct(self, data):
                    return self.autoencoder.predict(data)







        class ReinforcementLearning:



            class ModelFree:

                class QLearningAgent:
                    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.95, exploration_rate=1.0, exploration_decay=0.995, min_exploration_rate=0.01):
                        self.state_size = state_size
                        self.action_size = action_size
                        self.learning_rate = learning_rate
                        self.discount_factor = discount_factor
                        self.exploration_rate = exploration_rate
                        self.exploration_decay = exploration_decay
                        self.min_exploration_rate = min_exploration_rate
                        self.q_table = np.zeros((state_size, action_size))

                    def choose_action(self, state):
                        if random.uniform(0, 1) < self.exploration_rate:
                            return random.randint(0, self.action_size - 1)  # انتخاب تصادفی
                        else:
                            return np.argmax(self.q_table[state])  # انتخاب بهترین عمل

                    def update_q_value(self, state, action, reward, next_state):
                        best_next_action = np.argmax(self.q_table[next_state])
                        td_target = reward + self.discount_factor * self.q_table[next_state][best_next_action]
                        td_delta = td_target - self.q_table[state][action]
                        self.q_table[state][action] += self.learning_rate * td_delta

                    def decay_exploration(self):
                        if self.exploration_rate > self.min_exploration_rate:
                            self.exploration_rate *= self.exploration_decay

                    def train(self, episodes, env):
                        for episode in range(episodes):
                            state = env.reset()  # ریست محیط و دریافت حالت اولیه
                            done = False
                            
                            while not done:
                                action = self.choose_action(state)
                                next_state, reward, done, _ = env.step(action)  # اجرای عمل و دریافت حالت بعدی و پاداش
                                self.update_q_value(state, action, reward, next_state)
                                state = next_state
                            
                            self.decay_exploration()  # کاهش نرخ اکتشاف پس از هر اپیزود


            





            class ModelBased:

                class SARSA:
                    def __init__(self, num_states, num_actions, alpha=0.1, gamma=0.9, epsilon=0.1):
                        self.num_states = num_states
                        self.num_actions = num_actions
                        self.alpha = alpha  # نرخ یادگیری
                        self.gamma = gamma  # فاکتور تخفیف
                        self.epsilon = epsilon  # نرخ اکتشاف

                        # Q-مقدارها را با صفرها مقداردهی اولیه می‌کنیم
                        self.Q = np.zeros((num_states, num_actions))

                    def choose_action(self, state):
                        # با احتمال epsilon یک عمل تصادفی انتخاب می‌کنیم
                        if np.random.rand() < self.epsilon:
                            return np.random.choice(self.num_actions)
                        else:
                            return np.argmax(self.Q[state])

                    def update(self, state, action, reward, next_state, next_action):
                        # به‌روزرسانی Q-مقدار با استفاده از فرمول SARSA
                        td_target = reward + self.gamma * self.Q[next_state][next_action]
                        td_delta = td_target - self.Q[state][action]
                        self.Q[state][action] += self.alpha * td_delta

                    def train(self, env, num_episodes):
                        for episode in range(num_episodes):
                            state = env.reset()  # محیط را ریست می‌کنیم
                            action = self.choose_action(state)

                            done = False
                            while not done:
                                next_state, reward, done, _ = env.step(action)  # عمل را در محیط انجام می‌دهیم
                                next_action = self.choose_action(next_state)  # عمل بعدی را انتخاب می‌کنیم
                                self.update(state, action, reward, next_state, next_action)  # Q-مقادیر را به‌روزرسانی می‌کنیم
                                
                                state, action = next_state, next_action  # وضعیت و عمل را به‌روزرسانی می‌کنیم

                    def get_q_values(self):
                        return self.Q

































    class DeeperAIModels:

        class ComputerVision:

            def __init__(self):
                self.faceProto = "opencv_face_detector.pbtxt"
                self.faceModel = "opencv_face_detector_uint8.pb"
                self.ageProto = "age_deploy.prototxt"
                self.ageModel = "age_net.caffemodel"
                self.genderProto = "gender_deploy.prototxt"
                self.genderModel = "gender_net.caffemodel"

                self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
                self.ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
                self.genderList = ['Male', 'Female']

                self.faceNet = cv2.dnn.readNet(self.faceModel, self.faceProto)
                self.ageNet = cv2.dnn.readNet(self.ageModel, self.ageProto)
                self.genderNet = cv2.dnn.readNet(self.genderModel, self.genderProto)

            def highlight_face(self, frame, conf_threshold=0.7):
                frame_opencv_dnn = frame.copy()
                frame_height = frame_opencv_dnn.shape[0]
                frame_width = frame_opencv_dnn.shape[1]
                blob = cv2.dnn.blobFromImage(frame_opencv_dnn, 1.0, (300, 300), [104, 117, 123], True, False)

                self.faceNet.setInput(blob)
                detections = self.faceNet.forward()
                face_boxes = []
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    if confidence > conf_threshold:
                        x1 = int(detections[0, 0, i, 3] * frame_width)
                        y1 = int(detections[0, 0, i, 4] * frame_height)
                        x2 = int(detections[0, 0, i, 5] * frame_width)
                        y2 = int(detections[0, 0, i, 6] * frame_height)
                        face_boxes.append([x1, y1, x2, y2])
                        cv2.rectangle(frame_opencv_dnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frame_height / 150)), 8)
                return frame_opencv_dnn, face_boxes

            def detect_age_and_gender(self, frame, padding=20):
                result_img, face_boxes = self.highlight_face(frame)
                detected_info = []

                if not face_boxes:
                    print("No face detected")
                    return result_img, detected_info

                for face_box in face_boxes:
                    face = frame[max(0, face_box[1] - padding):
                                 min(face_box[3] + padding, frame.shape[0] - 1),
                                 max(0, face_box[0] - padding):
                                 min(face_box[2] + padding, frame.shape[1] - 1)]

                    blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)

                    self.genderNet.setInput(blob)
                    gender_preds = self.genderNet.forward()
                    gender = self.genderList[gender_preds[0].argmax()]

                    self.ageNet.setInput(blob)
                    age_preds = self.ageNet.forward()
                    age = self.ageList[age_preds[0].argmax()]

                    detected_info.append({
                        "gender": gender,
                        "age": age[1:-1],
                        "coordinates": face_box
                    })

                    cv2.putText(result_img, f"{gender}, {age}", (face_box[0], face_box[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

                return result_img, detected_info

            def detect_from_image(self, image_path):
                frame = cv2.imread(image_path)
                if frame is None:
                    raise Exception("Failed to load image from the specified path.")
                return self.detect_age_and_gender(frame)

            def detect_from_webcam(self):
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    raise Exception("Failed to access webcam.")

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    result_img, detected_info = self.detect_age_and_gender(frame)
                    print(detected_info)
                    cv2.imshow("Age and Gender Detection", result_img)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                cap.release()
                cv2.destroyAllWindows()

            def save_results(self, frame, detected_info, save_path):
                cv2.imwrite(save_path, frame)
                with open(f"{save_path}.txt", "w") as f:
                    for info in detected_info:
                        f.write(str(info) + "\n")

            def get_webcam_photo(self):
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                if not ret:
                    raise Exception("Failed to capture photo from webcam.")
                return frame

            def find_objects(self, frame):
                net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
                layer_names = net.getLayerNames()
                output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
                with open("coco.names", "r") as f:
                    classes = [line.strip() for line in f.readlines()]

                height, width, channels = frame.shape
                blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                detections = net.forward(output_layers)

                objects_info = []
                for det in detections:
                    for obj in det:
                        scores = obj[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]

                        if confidence > 0.5:
                            center_x = int(obj[0] * width)
                            center_y = int(obj[1] * height)
                            w = int(obj[2] * width)
                            h = int(obj[3] * height)

                            relative_distance = round(1 / (w * h), 2)

                            label = str(classes[class_id])
                            objects_info.append({"label": label, "confidence": confidence, "relative_distance": relative_distance})

                            x = int(center_x - w / 2)
                            y = int(center_y - h / 2)
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(frame, f"{label} {confidence:.2f} dist:{relative_distance}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                return objects_info