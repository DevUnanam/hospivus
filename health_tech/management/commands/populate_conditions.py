import os
import requests
from io import BytesIO
from PIL import Image
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from health_tech.models import MedicalCondition


class Command(BaseCommand):
    help = 'Populate the database with sample medical conditions'

    def handle(self, *args, **options):
        """
        Populate the database with comprehensive medical conditions data.
        Creates realistic medical conditions across different departments.
        """
        self.stdout.write(self.style.SUCCESS('Starting to populate medical conditions...'))

        # Sample medical conditions data
        conditions_data = [
            # Cardiology
            {
                'name': 'Atrial Fibrillation',
                'overview': 'Atrial fibrillation (AFib) is an irregular and often very rapid heart rhythm that can lead to blood clots in the heart. AFib increases the risk of stroke, heart failure and other heart-related complications.',
                'symptoms': 'Symptoms may include heart palpitations, shortness of breath, weakness, chest pain, dizziness, fatigue, lightheadedness, reduced ability to exercise, and confusion.',
                'causes': 'Risk factors include age, high blood pressure, underlying heart disease, drinking alcohol, family history, sleep apnea, and other chronic conditions.',
                'treatments': 'Treatment may include medications to control heart rate and rhythm, blood thinners to prevent stroke, cardioversion, catheter procedures, and surgery in some cases.',
                'department': 'cardiology',
                'image_url': 'https://via.placeholder.com/400x300/FF6B6B/FFFFFF?text=Atrial+Fibrillation'
            },
            {
                'name': 'Angina',
                'overview': 'Angina is chest pain caused by reduced blood flow to the heart muscles. Angina is a symptom of coronary artery disease.',
                'symptoms': 'Chest pain or discomfort, pain in arms, neck, jaw, shoulder or back, nausea, fatigue, shortness of breath, sweating, dizziness.',
                'causes': 'Coronary artery disease, caused by atherosclerosis, plaque buildup in arteries, reduced blood flow to heart muscle.',
                'treatments': 'Lifestyle changes, medications (nitrates, beta-blockers, calcium channel blockers), angioplasty, coronary artery bypass surgery.',
                'department': 'cardiology',
                'image_url': 'https://via.placeholder.com/400x300/FF6B6B/FFFFFF?text=Angina'
            },

            # Neurology
            {
                'name': 'Alzheimer\'s Disease',
                'overview': 'Alzheimer\'s disease is a progressive neurologic disorder that causes the brain to shrink and brain cells to die. It is the most common cause of dementia.',
                'symptoms': 'Memory loss, difficulty thinking and problem-solving, challenges completing familiar tasks, confusion with time or place, trouble understanding visual images, problems with speaking or writing.',
                'causes': 'Age, family history, genetics, head trauma, lifestyle factors, and cardiovascular disease may contribute to the development of Alzheimer\'s.',
                'treatments': 'Current treatments focus on maintaining mental function, managing behavioral symptoms, and slowing disease progression. Medications and supportive care are primary approaches.',
                'department': 'neurology',
                'image_url': 'https://via.placeholder.com/400x300/4ECDC4/FFFFFF?text=Alzheimer\'s+Disease'
            },
            {
                'name': 'Brain Aneurysm',
                'overview': 'A brain aneurysm is a bulge or ballooning in a blood vessel in the brain. It often looks like a berry hanging on a stem.',
                'symptoms': 'Ruptured aneurysm: sudden severe headache, nausea, vomiting, stiff neck, blurred vision, sensitivity to light, seizure, loss of consciousness.',
                'causes': 'Risk factors include smoking, high blood pressure, drug abuse, family history, age, and certain genetic conditions.',
                'treatments': 'Treatment depends on size and location. Options include surgical clipping, endovascular coiling, flow diverters, and monitoring for small aneurysms.',
                'department': 'neurology',
                'image_url': 'https://via.placeholder.com/400x300/4ECDC4/FFFFFF?text=Brain+Aneurysm'
            },

            # Endocrinology
            {
                'name': 'Diabetes Mellitus',
                'overview': 'Diabetes mellitus refers to a group of diseases that result in too much sugar in the blood (high blood glucose).',
                'symptoms': 'Increased thirst, frequent urination, hunger, fatigue, blurred vision, slow-healing sores, frequent infections, unexplained weight loss.',
                'causes': 'Type 1: autoimmune destruction of insulin-producing cells. Type 2: insulin resistance and relative insulin deficiency. Risk factors include genetics, obesity, and lifestyle.',
                'treatments': 'Type 1: insulin therapy, blood sugar monitoring, carbohydrate counting. Type 2: lifestyle changes, oral medications, insulin when needed.',
                'department': 'endocrinology',
                'image_url': 'https://via.placeholder.com/400x300/45B7D1/FFFFFF?text=Diabetes'
            },

            # Pulmonology
            {
                'name': 'Chronic Obstructive Pulmonary Disease',
                'overview': 'COPD is a chronic inflammatory lung disease that causes obstructed airflow from the lungs. It includes emphysema and chronic bronchitis.',
                'symptoms': 'Shortness of breath, wheezing, chest tightness, chronic cough with mucus, frequent respiratory infections, fatigue, swelling in ankles, feet or legs.',
                'causes': 'Long-term exposure to irritating gases or particulate matter, most often from cigarette smoke. Air pollution, chemical fumes, and dust can also contribute.',
                'treatments': 'Bronchodilators, inhaled steroids, pulmonary rehabilitation, oxygen therapy, lifestyle changes, and in severe cases, surgery.',
                'department': 'pulmonology',
                'image_url': 'https://via.placeholder.com/400x300/96CEB4/FFFFFF?text=COPD'
            },

            # Dermatology
            {
                'name': 'Eczema',
                'overview': 'Eczema (atopic dermatitis) is a condition that makes your skin red and itchy. It\'s common in children but can occur at any age.',
                'symptoms': 'Dry skin, itching, red to brownish-gray patches, small raised bumps, thick cracked scaly skin, raw sensitive swollen skin from scratching.',
                'causes': 'Genetics, immune system dysfunction, environmental triggers, stress, irritants, allergens, and hormonal changes.',
                'treatments': 'Moisturizers, topical corticosteroids, calcineurin inhibitors, antihistamines, phototherapy, and avoiding known triggers.',
                'department': 'dermatology',
                'image_url': 'https://via.placeholder.com/400x300/FFEAA7/333333?text=Eczema'
            },

            # Gastroenterology
            {
                'name': 'Gastroesophageal Reflux Disease',
                'overview': 'GERD is a chronic digestive disease that occurs when stomach acid or bile flows back into the food pipe and irritates the lining.',
                'symptoms': 'Heartburn, regurgitation of food or sour liquid, difficulty swallowing, chest pain, chronic cough, laryngitis, disrupted sleep.',
                'causes': 'Hiatal hernia, pregnancy, smoking, obesity, certain foods and drinks, medications, and delayed stomach emptying.',
                'treatments': 'Lifestyle changes, antacids, H2 receptor blockers, proton pump inhibitors, surgery in severe cases.',
                'department': 'gastroenterology',
                'image_url': 'https://via.placeholder.com/400x300/DDA0DD/FFFFFF?text=GERD'
            },

            # Orthopedics
            {
                'name': 'Osteoarthritis',
                'overview': 'Osteoarthritis is the most common form of arthritis, affecting millions worldwide. It occurs when protective cartilage on the ends of bones wears down over time.',
                'symptoms': 'Joint pain, stiffness, tenderness, loss of flexibility, grating sensation, bone spurs, swelling around the joint.',
                'causes': 'Age, obesity, joint injuries, genetics, bone deformities, certain metabolic diseases, and repetitive stress on joints.',
                'treatments': 'Exercise, weight management, physical therapy, medications, injections, assistive devices, and in severe cases, surgery.',
                'department': 'orthopedics',
                'image_url': 'https://via.placeholder.com/400x300/74B9FF/FFFFFF?text=Osteoarthritis'
            },

            # Oncology
            {
                'name': 'Breast Cancer',
                'overview': 'Breast cancer occurs when cells in breast tissue grow uncontrollably. It\'s the second most common cancer in women, but it can also occur in men.',
                'symptoms': 'Breast lump, change in breast size or shape, dimpling of breast skin, nipple discharge, red or flaky nipple or breast skin.',
                'causes': 'Risk factors include age, gender, family history, genetic mutations (BRCA1/BRCA2), lifestyle factors, and hormonal influences.',
                'treatments': 'Surgery, chemotherapy, radiation therapy, hormone therapy, targeted therapy, and immunotherapy, depending on the stage and type.',
                'department': 'oncology',
                'image_url': 'https://via.placeholder.com/400x300/FD79A8/FFFFFF?text=Breast+Cancer'
            },

            # Additional conditions across different letters
            {
                'name': 'Fibromyalgia',
                'overview': 'Fibromyalgia is a disorder characterized by widespread musculoskeletal pain accompanied by fatigue, sleep, memory and mood issues.',
                'symptoms': 'Widespread pain, fatigue, sleep disturbances, cognitive difficulties, morning stiffness, headaches, irritable bowel syndrome.',
                'causes': 'The exact cause is unknown, but factors include genetics, infections, physical or emotional trauma, and stress.',
                'treatments': 'Medications (pain relievers, antidepressants), therapy, stress management, exercise, sleep hygiene, and alternative treatments.',
                'department': 'rheumatology',
                'image_url': 'https://via.placeholder.com/400x300/A29BFE/FFFFFF?text=Fibromyalgia'
            },
            {
                'name': 'Hypertension',
                'overview': 'High blood pressure is a common condition in which the long-term force of blood against artery walls is high enough to cause health problems.',
                'symptoms': 'Often called "silent killer" as it usually has no symptoms. In severe cases: headaches, shortness of breath, nosebleeds.',
                'causes': 'Age, race, family history, obesity, lack of physical activity, tobacco use, too much salt, stress, chronic kidney disease.',
                'treatments': 'Lifestyle changes (diet, exercise, weight loss), medications (ACE inhibitors, diuretics, beta-blockers, calcium channel blockers).',
                'department': 'cardiology',
                'image_url': 'https://via.placeholder.com/400x300/00B894/FFFFFF?text=Hypertension'
            },
            {
                'name': 'Insomnia',
                'overview': 'Insomnia is a common sleep disorder that can make it hard to fall asleep, hard to stay asleep, or cause you to wake up too early.',
                'symptoms': 'Difficulty falling asleep, waking up often during the night, waking up too early, not feeling well-rested, daytime tiredness.',
                'causes': 'Stress, travel, work schedule, poor sleep habits, eating too much late in evening, mental health disorders, medications.',
                'treatments': 'Sleep hygiene education, cognitive behavioral therapy, relaxation techniques, medications, treating underlying conditions.',
                'department': 'psychiatry',
                'image_url': 'https://via.placeholder.com/400x300/6C5CE7/FFFFFF?text=Insomnia'
            },
            {
                'name': 'Kidney Stones',
                'overview': 'Kidney stones are hard deposits made of minerals and salts that form inside your kidneys.',
                'symptoms': 'Severe pain in side and back, pain that radiates to lower abdomen and groin, painful urination, pink/red/brown urine.',
                'causes': 'Diet, excess body weight, medical conditions, certain supplements and medications, dehydration.',
                'treatments': 'Pain management, drinking water, medical therapy to pass stones, shock wave lithotripsy, surgery for large stones.',
                'department': 'nephrology',
                'image_url': 'https://via.placeholder.com/400x300/FDCB6E/333333?text=Kidney+Stones'
            },
            {
                'name': 'Migraine',
                'overview': 'A migraine is a headache that can cause severe throbbing pain or a pulsing sensation, usually on one side of the head.',
                'symptoms': 'Severe headache, nausea, vomiting, sensitivity to light and sound, visual disturbances (aura), tingling in face/hands.',
                'causes': 'Hormonal changes, foods, stress, sensory stimuli, sleep changes, physical factors, medications, weather changes.',
                'treatments': 'Pain-relieving medications, preventive medications, lifestyle changes, alternative treatments, avoiding triggers.',
                'department': 'neurology',
                'image_url': 'https://via.placeholder.com/400x300/E17055/FFFFFF?text=Migraine'
            },
            {
                'name': 'Pneumonia',
                'overview': 'Pneumonia is an infection that inflames air sacs in one or both lungs, which may fill with fluid.',
                'symptoms': 'Cough with phlegm, fever, chills, difficulty breathing, chest pain when breathing or coughing, fatigue.',
                'causes': 'Bacteria, viruses, fungi. Can be community-acquired, hospital-acquired, or healthcare-associated.',
                'treatments': 'Antibiotics for bacterial pneumonia, antiviral medications, antifungal medications, supportive care, hospitalization if severe.',
                'department': 'pulmonology',
                'image_url': 'https://via.placeholder.com/400x300/00CEC9/FFFFFF?text=Pneumonia'
            },
            {
                'name': 'Stroke',
                'overview': 'A stroke occurs when blood supply to part of your brain is interrupted or reduced, preventing brain tissue from getting oxygen.',
                'symptoms': 'Sudden numbness or weakness, confusion, trouble speaking, difficulty seeing, trouble walking, dizziness, severe headache.',
                'causes': 'Blocked artery (ischemic stroke), leaking or bursting blood vessel (hemorrhagic stroke). Risk factors include hypertension, smoking, diabetes.',
                'treatments': 'Emergency treatment with clot-busting drugs, mechanical thrombectomy, supportive care, rehabilitation, prevention of future strokes.',
                'department': 'neurology',
                'image_url': 'https://via.placeholder.com/400x300/2D3436/FFFFFF?text=Stroke'
            },
            {
                'name': 'Thyroid Cancer',
                'overview': 'Thyroid cancer occurs in the cells of the thyroid gland, located at the base of your neck, below your Adam\'s apple.',
                'symptoms': 'Lump in neck, changes to voice/hoarseness, difficulty swallowing, pain in neck and throat, swollen lymph nodes.',
                'causes': 'Risk factors include being female, exposure to radiation, certain inherited genetic syndromes, iodine deficiency.',
                'treatments': 'Surgery, radioactive iodine therapy, thyroid hormone therapy, external beam radiation, chemotherapy, targeted drug therapy.',
                'department': 'oncology',
                'image_url': 'https://via.placeholder.com/400x300/81ECEC/333333?text=Thyroid+Cancer'
            },
            {
                'name': 'Urinary Tract Infection',
                'overview': 'A UTI is an infection in any part of your urinary system — kidneys, ureters, bladder and urethra.',
                'symptoms': 'Strong urge to urinate, burning sensation when urinating, cloudy urine, strong-smelling urine, pelvic pain in women.',
                'causes': 'Bacteria entering the urinary tract through the urethra. Risk factors include female anatomy, sexual activity, birth control.',
                'treatments': 'Antibiotics are the main treatment. Drinking plenty of fluids, pain relievers, preventing recurrent infections.',
                'department': 'urology',
                'image_url': 'https://via.placeholder.com/400x300/FAB1A0/333333?text=UTI'
            },
            {
                'name': 'Varicose Veins',
                'overview': 'Varicose veins are enlarged, twisted veins that commonly occur in the legs and feet.',
                'symptoms': 'Dark blue or purple veins, twisted and bulging appearance, aching pain, heavy feeling in legs, swelling, skin changes.',
                'causes': 'Weak or damaged valves in veins. Risk factors include age, gender, pregnancy, family history, obesity, prolonged standing.',
                'treatments': 'Compression stockings, lifestyle changes, sclerotherapy, laser treatments, radiofrequency ablation, surgical options.',
                'department': 'general_surgery',
                'image_url': 'https://via.placeholder.com/400x300/FF7675/FFFFFF?text=Varicose+Veins'
            }
        ]

        created_count = 0
        
        for condition_data in conditions_data:
            # Check if condition already exists
            if MedicalCondition.objects.filter(name=condition_data['name']).exists():
                self.stdout.write(self.style.WARNING(f'Condition "{condition_data["name"]}" already exists, skipping...'))
                continue

            # Create the condition
            condition = MedicalCondition(
                name=condition_data['name'],
                overview=condition_data['overview'],
                symptoms=condition_data['symptoms'],
                causes=condition_data['causes'],
                treatments=condition_data['treatments'],
                department=condition_data['department']
            )

            # Download and save image if URL is provided
            if 'image_url' in condition_data and condition_data['image_url']:
                try:
                    self.stdout.write(f'Downloading image for {condition_data["name"]}...')
                    response = requests.get(condition_data['image_url'], timeout=10)
                    response.raise_for_status()
                    
                    # Create a simple image file
                    img_content = ContentFile(response.content)
                    clean_name = condition_data['name'].lower().replace(' ', '_').replace("'", '')
                    img_filename = f"{clean_name}.jpg"
                    condition.image.save(img_filename, img_content, save=False)
                    
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed to download image for {condition_data["name"]}: {str(e)}'))

            condition.save()
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'Created condition: {condition.name}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} medical conditions!\n'
                f'Total conditions in database: {MedicalCondition.objects.count()}'
            )
        )