import os
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from health_tech.models import MedicalCondition
from PIL import Image, ImageDraw, ImageFont


class Command(BaseCommand):
    help = 'Populate the database with sample medical conditions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing conditions before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing medical conditions...')
            MedicalCondition.objects.all().delete()

        self.stdout.write('Populating medical conditions database...')
        
        # Sample medical conditions data
        conditions_data = [
            # A
            {
                'name': 'Asthma',
                'department': 'pulmonology',
                'overview': 'Asthma is a condition in which your airways narrow and swell and may produce extra mucus. This can make breathing difficult and trigger coughing, a whistling sound (wheezing) when you breathe out and shortness of breath.',
                'symptoms': 'Shortness of breath, chest tightness or pain, wheezing when exhaling (especially in children), trouble sleeping due to shortness of breath, coughing or wheezing attacks worsened by respiratory virus.',
                'causes': 'Airborne allergens (pollen, dust mites, mold spores, pet dander), respiratory infections, physical activity, cold air, air pollutants and irritants, strong emotions and stress, sulfites in food and drinks.',
                'treatments': 'Quick-relief medications (rescue inhalers), long-term control medications, allergy medications, bronchial thermoplasty for severe asthma, lifestyle modifications including trigger avoidance.'
            },
            {
                'name': 'Arthritis',
                'department': 'rheumatology',
                'overview': 'Arthritis is the swelling and tenderness of one or more joints. The main symptoms are joint pain and stiffness, which typically worsen with age. The most common types are osteoarthritis and rheumatoid arthritis.',
                'symptoms': 'Pain, stiffness, swelling in and around joints, decreased range of motion, redness around the joint, warmth around the joint, fatigue, loss of appetite.',
                'causes': 'Age, gender (women more likely), genetics, previous joint injury, obesity, certain occupations requiring repetitive motions, autoimmune disorders.',
                'treatments': 'Medications (NSAIDs, corticosteroids, DMARDs), physical therapy, occupational therapy, joint replacement surgery, lifestyle modifications, weight management.'
            },
            {
                'name': 'Anxiety Disorders',
                'department': 'psychiatry',
                'overview': 'Anxiety disorders are a group of mental health conditions characterized by significant feelings of anxiety and fear. Anxiety is a normal emotion, but anxiety disorders involve more than temporary worry or fear.',
                'symptoms': 'Feeling nervous or restless, having a sense of impending danger, increased heart rate, breathing rapidly, sweating, trembling, difficulty concentrating, trouble sleeping, gastrointestinal problems.',
                'causes': 'Brain chemistry, genetics, environmental stressors, medical conditions, substance abuse, certain medications, traumatic events.',
                'treatments': 'Psychotherapy (cognitive behavioral therapy, exposure therapy), medications (antidepressants, anti-anxiety medications), lifestyle changes, relaxation techniques, stress management.'
            },
            
            # B
            {
                'name': 'Bipolar Disorder',
                'department': 'psychiatry',
                'overview': 'Bipolar disorder is a mental health condition that causes extreme mood swings that include emotional highs (mania or hypomania) and lows (depression). These mood swings can affect sleep, energy, activity, judgment, behavior and thinking.',
                'symptoms': 'Manic episodes: elevated mood, increased activity, decreased sleep, grandiosity, rapid speech. Depressive episodes: sad mood, loss of interest, fatigue, feelings of worthlessness.',
                'causes': 'Genetics, brain structure and functioning, environmental factors such as stress, traumatic events, major life changes.',
                'treatments': 'Mood stabilizers, antipsychotic medications, antidepressants, psychotherapy, electroconvulsive therapy (ECT), lifestyle management, support groups.'
            },
            {
                'name': 'Bronchitis',
                'department': 'pulmonology',
                'overview': 'Bronchitis is an inflammation of the bronchial tubes, which carry air to your lungs. It can be acute (lasting a few weeks) or chronic (lasting for months and recurring over years).',
                'symptoms': 'Cough that produces mucus, fatigue, shortness of breath, slight fever and chills, chest discomfort, sore throat, body aches.',
                'causes': 'Viral infections (most common for acute bronchitis), bacterial infections, smoking, exposure to irritants like air pollution, dust, vapors, fumes.',
                'treatments': 'Rest, fluids, humidifiers, cough suppressants, bronchodilators for breathing difficulties, antibiotics if bacterial, smoking cessation.'
            },
            
            # C
            {
                'name': 'Coronary Artery Disease',
                'department': 'cardiology',
                'overview': 'Coronary artery disease occurs when major blood vessels that supply the heart become damaged or diseased, usually due to plaque buildup. It is the most common type of heart disease.',
                'symptoms': 'Chest pain (angina), shortness of breath, fatigue, heart attack symptoms (severe chest pain, pain radiating to arms, neck, jaw), irregular heartbeat.',
                'causes': 'High cholesterol, high blood pressure, diabetes, smoking, obesity, physical inactivity, age, gender, family history, stress.',
                'treatments': 'Lifestyle changes, medications (statins, beta-blockers, ACE inhibitors), angioplasty and stent placement, coronary artery bypass surgery, cardiac rehabilitation.'
            },
            {
                'name': 'Chronic Kidney Disease',
                'department': 'nephrology',
                'overview': 'Chronic kidney disease is the gradual loss of kidney function over time. In advanced stages, dangerous levels of fluid, electrolytes and wastes can build up in the body.',
                'symptoms': 'Nausea, vomiting, loss of appetite, fatigue, sleep problems, decreased urine output, muscle cramps, swelling of feet and ankles, persistent itching.',
                'causes': 'Diabetes, high blood pressure, glomerulonephritis, polycystic kidney disease, urinary tract obstructions, certain medications, genetic disorders.',
                'treatments': 'Blood pressure control, diabetes management, dietary changes, medications to treat complications, dialysis, kidney transplant in end-stage disease.'
            },
            {
                'name': 'Celiac Disease',
                'department': 'gastroenterology',
                'overview': 'Celiac disease is an immune reaction to eating gluten, a protein found in wheat, barley and rye. It triggers inflammation that damages the small intestine lining.',
                'symptoms': 'Diarrhea, fatigue, weight loss, bloating, gas, abdominal pain, nausea, vomiting, skin rash, iron deficiency anemia, delayed growth in children.',
                'causes': 'Genetic predisposition combined with environmental triggers such as infection, surgery, pregnancy, childbirth, severe emotional stress.',
                'treatments': 'Strict gluten-free diet for life, nutritional supplements to address deficiencies, treatment of complications, regular monitoring by healthcare providers.'
            },
            
            # D
            {
                'name': 'Diabetes Type 2',
                'department': 'endocrinology',
                'overview': 'Type 2 diabetes is a chronic condition that affects how your body processes glucose. Your body either resists the effects of insulin or does not produce enough insulin to maintain normal glucose levels.',
                'symptoms': 'Increased thirst, frequent urination, increased hunger, unintended weight loss, fatigue, blurred vision, slow-healing sores, frequent infections.',
                'causes': 'Genetics, obesity, physical inactivity, age (45 and older), race and ethnicity, high blood pressure, abnormal cholesterol levels, history of gestational diabetes.',
                'treatments': 'Lifestyle modifications (diet and exercise), medications (metformin, insulin, other antidiabetic drugs), blood glucose monitoring, regular medical check-ups.'
            },
            {
                'name': 'Depression',
                'department': 'psychiatry',
                'overview': 'Depression is a mood disorder that causes persistent feelings of sadness and loss of interest. It affects how you feel, think and behave and can lead to various emotional and physical problems.',
                'symptoms': 'Persistent sad mood, loss of interest in activities, fatigue, sleep disturbances, appetite changes, feelings of worthlessness, difficulty concentrating, thoughts of death.',
                'causes': 'Brain chemistry, genetics, hormones, environmental factors, trauma, medical conditions, certain medications, substance abuse.',
                'treatments': 'Psychotherapy (cognitive behavioral therapy, interpersonal therapy), antidepressant medications, electroconvulsive therapy, lifestyle changes, support groups.'
            },
            
            # E
            {
                'name': 'Epilepsy',
                'department': 'neurology',
                'overview': 'Epilepsy is a neurological disorder in which brain activity becomes abnormal, causing seizures or periods of unusual behavior, sensations and sometimes loss of awareness.',
                'symptoms': 'Seizures (can vary from brief staring spells to severe convulsions), temporary confusion, uncontrollable jerking movements, loss of consciousness, fear, anxiety.',
                'causes': 'Genetic influence, head trauma, brain infections, prenatal injury, developmental disorders, stroke, brain tumors.',
                'treatments': 'Anti-seizure medications, vagus nerve stimulation, ketogenic diet, brain surgery in severe cases, lifestyle modifications.'
            },
            {
                'name': 'Eczema',
                'department': 'dermatology',
                'overview': 'Eczema is a group of conditions that cause the skin to become red, itchy and inflamed. Atopic dermatitis is the most common form and is often associated with allergies and asthma.',
                'symptoms': 'Itchy skin, red to brownish-gray patches, small raised bumps, thickened cracked skin, sensitive swollen skin from scratching, dry scaly skin.',
                'causes': 'Genetics, environmental triggers (allergens, irritants, stress), immune system dysfunction, dry skin, bacterial infections.',
                'treatments': 'Moisturizers, topical corticosteroids, topical calcineurin inhibitors, antihistamines, antibiotics for infections, phototherapy, immunosuppressants.'
            },
            
            # F
            {
                'name': 'Fibromyalgia',
                'department': 'rheumatology',
                'overview': 'Fibromyalgia is a disorder characterized by widespread musculoskeletal pain accompanied by fatigue, sleep, memory and mood issues. It amplifies painful sensations.',
                'symptoms': 'Widespread pain, fatigue, sleep disturbances, cognitive difficulties (fibro fog), mood problems, headaches, irritable bowel syndrome.',
                'causes': 'Genetics, infections, physical or emotional trauma, stress, abnormal pain perception processing in the brain.',
                'treatments': 'Medications (pain relievers, antidepressants, anti-seizure drugs), exercise, stress management, sleep hygiene, cognitive behavioral therapy, alternative therapies.'
            },
            
            # G
            {
                'name': 'Gastroesophageal Reflux Disease (GERD)',
                'department': 'gastroenterology',
                'overview': 'GERD is a digestive disorder that occurs when acidic stomach juices or food and fluids back up from the stomach into the esophagus, causing heartburn and other symptoms.',
                'symptoms': 'Heartburn, acid regurgitation, difficulty swallowing, chest pain, chronic cough, sore throat, hoarse voice, feeling of lump in throat.',
                'causes': 'Hiatal hernia, pregnancy, obesity, smoking, certain foods and drinks, medications, delayed stomach emptying.',
                'treatments': 'Lifestyle modifications, antacids, H2 receptor blockers, proton pump inhibitors, prokinetic agents, surgery in severe cases.'
            },
            
            # H
            {
                'name': 'Hypertension',
                'department': 'cardiology',
                'overview': 'High blood pressure is a common condition in which the long-term force of blood against artery walls is high enough that it may eventually cause health problems like heart disease.',
                'symptoms': 'Often no symptoms (silent killer), headaches, dizziness, blurred vision, nausea, chest pain, shortness of breath in severe cases.',
                'causes': 'Age, genetics, obesity, high sodium intake, lack of physical activity, excessive alcohol, smoking, stress, chronic conditions.',
                'treatments': 'Lifestyle changes (diet, exercise, weight loss), ACE inhibitors, ARBs, diuretics, calcium channel blockers, beta-blockers, regular monitoring.'
            },
            {
                'name': 'Hypothyroidism',
                'department': 'endocrinology',
                'overview': 'Hypothyroidism is a condition in which the thyroid gland does not produce enough thyroid hormones, slowing down metabolism and affecting various body functions.',
                'symptoms': 'Fatigue, weight gain, cold intolerance, dry skin, hair loss, constipation, depression, memory problems, muscle weakness, slow heart rate.',
                'causes': 'Hashimoto thyroiditis, iodine deficiency, medications, radiation therapy, thyroid surgery, congenital conditions.',
                'treatments': 'Thyroid hormone replacement therapy (levothyroxine), regular monitoring of thyroid function tests, dietary considerations.'
            },
            
            # I
            {
                'name': 'Irritable Bowel Syndrome',
                'department': 'gastroenterology',
                'overview': 'IBS is a common disorder that affects the large intestine and causes cramping, abdominal pain, bloating, gas, and diarrhea or constipation, or both.',
                'symptoms': 'Abdominal pain and cramping, bloating, gas, diarrhea or constipation (sometimes both), mucus in stool, urgency to have bowel movements.',
                'causes': 'Abnormal gut muscle contractions, nervous system abnormalities, inflammation, severe infection, changes in gut bacteria, food intolerances.',
                'treatments': 'Dietary modifications (low-FODMAP diet), fiber supplements, medications (antispasmodics, laxatives, anti-diarrheal), probiotics, stress management.'
            },
            
            # M
            {
                'name': 'Migraine',
                'department': 'neurology',
                'overview': 'Migraine is a neurological condition that can cause multiple symptoms including intense, debilitating headaches. It often runs in families and affects people of all ages.',
                'symptoms': 'Severe throbbing headache (usually one-sided), nausea, vomiting, sensitivity to light and sound, visual disturbances (aura), fatigue.',
                'causes': 'Genetics, hormonal changes, certain foods, stress, sleep changes, physical factors, environmental changes, medications.',
                'treatments': 'Pain relief medications, preventive medications, lifestyle modifications, trigger avoidance, stress management, regular sleep patterns.'
            },
            
            # O
            {
                'name': 'Osteoporosis',
                'department': 'orthopedics',
                'overview': 'Osteoporosis is a bone disease that develops when bone mineral density decreases or when the quality or structure of bone changes, leading to increased fracture risk.',
                'symptoms': 'Often no symptoms until fracture occurs, back pain, loss of height, stooped posture, bone fractures that occur more easily than expected.',
                'causes': 'Aging, hormonal changes (especially estrogen decrease), genetics, low calcium and vitamin D intake, sedentary lifestyle, smoking, excessive alcohol.',
                'treatments': 'Calcium and vitamin D supplements, bisphosphonates, hormone therapy, lifestyle modifications, weight-bearing exercise, fall prevention.'
            },
            
            # P
            {
                'name': 'Pneumonia',
                'department': 'pulmonology',
                'overview': 'Pneumonia is an infection that inflames air sacs in one or both lungs, which may fill with fluid or pus, causing cough with phlegm, fever, chills, and difficulty breathing.',
                'symptoms': 'Cough with phlegm or pus, fever, chills, difficulty breathing, chest pain when breathing or coughing, fatigue, nausea, vomiting, diarrhea.',
                'causes': 'Bacteria, viruses, fungi, aspiration of food or liquids, weakened immune system, chronic diseases, smoking, recent respiratory infection.',
                'treatments': 'Antibiotics for bacterial pneumonia, antiviral medications, antifungal medications, supportive care, hospitalization in severe cases, vaccination prevention.'
            },
            
            # S
            {
                'name': 'Sleep Apnea',
                'department': 'pulmonology',
                'overview': 'Sleep apnea is a serious sleep disorder in which breathing repeatedly stops and starts during sleep. The most common type is obstructive sleep apnea.',
                'symptoms': 'Loud snoring, gasping for air during sleep, morning headache, excessive daytime sleepiness, difficulty concentrating, irritability, high blood pressure.',
                'causes': 'Obesity, large neck circumference, narrowed airways, male gender, older age, family history, smoking, alcohol use, nasal congestion.',
                'treatments': 'CPAP (continuous positive airway pressure) therapy, lifestyle changes, oral appliances, surgery, weight loss, positional therapy.'
            },
            
            # U
            {
                'name': 'Urinary Tract Infection',
                'department': 'urology',
                'overview': 'A urinary tract infection is an infection in any part of the urinary system including kidneys, bladder, ureters, and urethra. Most infections involve the lower urinary tract.',
                'symptoms': 'Strong, persistent urge to urinate, burning sensation when urinating, frequent small amounts of urine, cloudy urine, pelvic pain in women.',
                'causes': 'Bacteria entering through the urethra, sexual activity, certain types of birth control, menopause, urinary tract abnormalities, blockages, suppressed immune system.',
                'treatments': 'Antibiotics, increased fluid intake, pain medication, cranberry products (limited evidence), proper hygiene, urinating after sexual activity.'
            }
        ]

        created_count = 0
        for condition_data in conditions_data:
            # Check if condition already exists
            if not MedicalCondition.objects.filter(name=condition_data['name']).exists():
                # Create a simple placeholder image
                image = self.create_placeholder_image(condition_data['name'])
                
                condition = MedicalCondition.objects.create(
                    name=condition_data['name'],
                    department=condition_data['department'],
                    overview=condition_data['overview'],
                    symptoms=condition_data['symptoms'],
                    causes=condition_data['causes'],
                    treatments=condition_data['treatments'],
                    image=image
                )
                created_count += 1
                self.stdout.write(f'Created: {condition.name}')
            else:
                self.stdout.write(f'Skipped (already exists): {condition_data["name"]}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated database with {created_count} medical conditions!'
            )
        )

    def create_placeholder_image(self, condition_name):
        """Create a placeholder image for the condition"""
        # Create a simple image with the first letter of the condition
        img = Image.new('RGB', (400, 300), color=(59, 130, 246))  # Blue background
        d = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 120)
        except:
            font = ImageFont.load_default()
        
        # Get the first letter
        letter = condition_name[0].upper()
        
        # Calculate position to center the text
        bbox = d.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (400 - text_width) // 2
        y = (300 - text_height) // 2
        
        # Draw the letter
        d.text((x, y), letter, fill=(255, 255, 255), font=font)
        
        # Save to BytesIO
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG', quality=85)
        img_buffer.seek(0)
        
        # Create Django file
        filename = f"{condition_name.lower().replace(' ', '_')}_placeholder.jpg"
        return SimpleUploadedFile(
            filename,
            img_buffer.read(),
            content_type='image/jpeg'
        )