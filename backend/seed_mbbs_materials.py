"""
Seeder for MBBS and Medical study materials.
Adds comprehensive clinical and para-clinical study materials for MBBS Year 2 / medical students.
"""
from typing import List
from sqlalchemy.orm import Session
from models import StudyMaterial, Student


def get_mbbs_materials_data() -> List[dict]:
    return [
        {
            "title": "General Pathology: Cellular Injury, Necrosis & Apoptosis",
            "subject": "Pathology",
            "topic": "Cellular Injury & Neoplasia",
            "course": "MBBS",
            "curriculum": "Pondicherry University",
            "academic_year": "Year 2",
            "material_type": "notes",
            "difficulty_level": "medium",
            "summary": "Coagulative, liquefactive, caseous, and fat necrosis; apoptotic signaling pathways; cellular adaptations (hyperplasia, hypertrophy, atrophy, metaplasia).",
            "content": """# General Pathology: Cellular Injury, Adaptations & Cell Death

## 1. Mechanisms of Cell Injury
- **Hypoxia and Ischemia**: Most common cause of cell injury. Results in decreased ATP synthesis, failure of the Na+/K+ ATPase pump, cellular swelling, and lactic acidosis.
- **Mitochondrial Damage**: Triggers opening of mitochondrial permeability transition pores and release of Cytochrome C, which activates caspase-mediated apoptosis.
- **Calcium Influx**: Elevated cytosolic Ca2+ activates phospholipases, proteases, endonucleases, and ATPases, accelerating irreversible damage.

## 2. Patterns of Tissue Necrosis
- **Coagulative Necrosis**: Denaturation of structural proteins and enzymes. Characteristic of infarcts in solid organs (heart, kidney, spleen) except the brain. Tissue architecture preserved ('tombstone' appearance).
- **Liquefactive Necrosis**: Enzymatic digestion of dead cells. Typical of hypoxic brain injury (cerebral infarcts) and focal bacterial/fungal infections (abscess formation).
- **Caseous Necrosis**: Cheesy, white appearance characteristic of *Mycobacterium tuberculosis* granulomas. Amorphous granular debris encircled by epithelioid histiocytes and Langhans giant cells.
- **Fat Necrosis**: Focal areas of fat destruction by activated lipases, typical of acute pancreatitis. Fatty acids combine with calcium to produce chalky-white deposits (**saponification**).
- **Fibrinoid Necrosis**: Seen in immune complex vasculitis (e.g., Polyarteritis Nodosa) and malignant hypertension. Pink, amorphous deposition in blood vessel walls.

## 3. Apoptosis vs. Necrosis
| Feature | Necrosis | Apoptosis |
|---|---|---|
| Cell Size | Enlarged (swelling) | Reduced (shrinkage) |
| Nucleus | Pyknosis → Karyorrhexis → Karyolysis | Fragmentation into nucleosome-size fragments |
| Plasma Membrane | Disrupted | Intact (altered structure with phosphatidylserine exposure) |
| Cellular Contents | Enzymatic leakage outside | Intact in apoptotic bodies |
| Adjacent Inflammation | **Frequent / Intense** | **Absent** |
| Physiologic Role | Invariably pathologic | Often physiologic (embryogenesis, hormonal turnover) |
""",
        },
        {
            "title": "Autonomic Pharmacology & Antihypertensive Regimens",
            "subject": "Pharmacology",
            "topic": "Autonomic Nervous System & Cardiovascular Drugs",
            "course": "MBBS",
            "curriculum": "Pondicherry University",
            "academic_year": "Year 2",
            "material_type": "notes",
            "difficulty_level": "medium",
            "summary": "Cholinergic and adrenergic receptors; beta-blockers, ACE inhibitors, ARBs, CCBs, and JNC/AHA emergency hypertensive crisis protocols.",
            "content": """# Autonomic Pharmacology & Cardiovascular Therapeutics

## 1. Autonomic Receptor Distribution & Actions
- **Alpha-1 (α1)**: Vascular smooth muscle contraction (vasoconstriction), pupillary dilator (mydriasis), bladder sphincter contraction. Gq-coupled (↑ IP3/DAG/Ca2+).
- **Alpha-2 (α2)**: Presynaptic sympathetic nerve terminals (inhibits NE release), pancreatic islet beta cells (↓ insulin). Gi-coupled (↓ cAMP). *Drug:* Clonidine, Methyldopa.
- **Beta-1 (β1)**: Heart (↑ heart rate, ↑ contractility, ↑ AV conduction velocity), JG cells of kidney (↑ renin release). Gs-coupled (↑ cAMP). *Antagonists:* Metoprolol, Atenolol, Esmolol.
- **Beta-2 (β2)**: Bronchial smooth muscle (bronchodilation), skeletal muscle vasculature (vasodilation), liver (glycogenolysis). Gs-coupled. *Agonists:* Salbutamol, Salmeterol.
- **Muscarinic (M2, M3)**: M2 on heart (↓ SA nodal rate, ↓ AV conduction via Gi); M3 on bronchi (bronchoconstriction, ↑ secretions) and bladder detrusor (contraction via Gq).

## 2. Antihypertensive First-Line Classes (AHA / JNC-8 Guidelines)
1. **ACE Inhibitors (ACEi)**: Enalapril, Ramipril, Lisinopril.
   - *MOA:* Inhibit angiotensin converting enzyme, reducing Angiotensin II and aldosterone; prevent bradykinin degradation.
   - *Adverse Effects:* Dry cough (bradykinin accumulation), hyperkalemia, angioedema, teratogenicity (contraindicated in pregnancy).
2. **Angiotensin Receptor Blockers (ARBs)**: Losartan, Telmisartan, Valsartan.
   - *MOA:* Block AT1 receptors. Same hemodynamic benefits as ACEi without dry cough.
3. **Calcium Channel Blockers (CCBs)**:
   - *Dihydropyridines (Amlodipine, Nifedipine):* Selective peripheral arterial vasodilation. AE: peripheral pedal edema, reflex tachycardia.
   - *Non-dihydropyridines (Verapamil, Diltiazem):* Cardiac depressants (negative inotrope, negative chronotrope). Contraindicated in AV block.
4. **Thiazide Diuretics**: Chlorthalidone, Hydrochlorothiazide.
   - *MOA:* Inhibit Na+/Cl- cotransporter in distal convoluted tubule. AE: hypokalemia, hyperuricemia, hyperglycemia.

## 3. Hypertensive Emergency vs. Urgency
- **Hypertensive Emergency**: BP > 180/120 mmHg **with acute end-organ damage** (encephalopathy, acute aortic dissection, pulmonary edema, acute renal failure).
  - *Treatment:* IV infusions (Labetalol, Nicardipine, Sodium Nitroprusside, Nitroglycerin). Reduce MAP by no more than 20–25% in the first hour to prevent ischemic stroke.
""",
        },
        {
            "title": "High-Yield Antimicrobial Therapy & Drug Resistance Pearls",
            "subject": "Pharmacology",
            "topic": "Chemotherapy & Antimicrobial Resistance",
            "course": "MBBS",
            "curriculum": "Pondicherry University",
            "academic_year": "Year 2",
            "material_type": "important_questions",
            "difficulty_level": "difficult",
            "summary": "Mechanisms of action, resistance patterns (MRSA, ESBL, CRE), toxicities (aminoglycosides, fluoroquinolones, vancomycin), and empirical regimens.",
            "content": """# Antimicrobial Chemotherapy & Resistance Mechanisms

## 1. Core Bacterial Target Sites
- **Cell Wall Synthesis Inhibitors**:
  - *Beta-lactams (Penicillins, Cephalosporins, Carbapenems, Monobactams):* Bind and inhibit penicillin-binding proteins (PBPs), halting transpeptidation.
  - *Glycopeptides (Vancomycin, Teicoplanin):* Bind D-Ala-D-Ala terminus of cell wall peptidoglycan precursors.
- **Protein Synthesis Inhibitors (30S and 50S Ribosomal Subunits)**:
  - *30S Subunit:* Aminoglycosides (Gentamicin, Amikacin - bactericidal, cause misreading of mRNA); Tetracyclines (Doxycycline - bacteriostatic, block tRNA attachment).
  - *50S Subunit:* Macrolides (Azithromycin, Clarithromycin - block transpeptidation/translocation); Chloramphenicol; Linezolid.
- **Nucleic Acid Synthesis Inhibitors**:
  - *DNA Gyrase / Topoisomerase IV:* Fluoroquinolones (Ciprofloxacin, Levofloxacin).
  - *RNA Polymerase:* Rifampicin (critical in anti-tubercular therapy).
  - *Folate Synthesis:* Sulfonamides (dihydropteroate synthase) + Trimethoprim (dihydrofolate reductase).

## 2. Key Resistance Mechanisms
1. **MRSA (Methicillin-Resistant Staphylococcus aureus)**: Altered PBP2a encoded by the *mecA* gene. Beta-lactams cannot bind. *Drug of choice:* Vancomycin, Daptomycin, Linezolid.
2. **ESBL (Extended-Spectrum Beta-Lactamases)**: Cleave cephalosporins and monobactams. Produced by *E. coli* and *Klebsiella pneumoniae*. *Drug of choice:* Carbapenems (Meropenem, Imipenem).
3. **VRE (Vancomycin-Resistant Enterococci)**: Substitution of D-Ala-D-Ala with D-Ala-D-Lac (*vanA* gene). *Drug of choice:* Linezolid, Daptomycin.

## 3. High-Yield Drug Toxicities
- **Aminoglycosides**: Nephrotoxicity (ATN) and irreversible Ototoxicity. Potentiated by Loop diuretics.
- **Vancomycin**: Red Man Syndrome (infusion-related histamine release; prevent by slowing infusion rate), Ototoxicity, Nephrotoxicity.
- **Fluoroquinolones**: Tendonitis and Achilles tendon rupture, QT prolongation, cartilage toxicity in children.
""",
        },
        {
            "title": "Clinical Bacteriology & Antimicrobial Susceptibility Testing",
            "subject": "Microbiology",
            "topic": "Bacteriology & Culture Techniques",
            "course": "MBBS",
            "curriculum": "Pondicherry University",
            "academic_year": "Year 2",
            "material_type": "notes",
            "difficulty_level": "medium",
            "summary": "Gram staining protocols; culture media differentiation (Blood, MacConkey, Chocolate Agar); Kirby-Bauer disk diffusion, and CLSI breakpoint interpretation.",
            "content": """# Clinical Bacteriology & Diagnostic Microbiology

## 1. Diagnostic Staining Procedures
- **Gram Stain**:
  - Crystal Violet (Primary stain, 1 min) → Gram's Iodine (Mordant, 1 min) → Acetone/Alcohol (Decolorizer, 10–15 sec) → Dilute Carbol Fuchsin or Safranin (Counterstain, 30 sec).
  - *Gram-Positive:* Thick peptidoglycan wall retains crystal violet-iodine complex (Purple/Blue).
  - *Gram-Negative:* High lipid outer membrane dissolves in acetone, releasing primary stain; takes up counterstain (Pink/Red).
- **Ziehl-Neelsen (Acid-Fast) Stain**:
  - Used for *Mycobacterium tuberculosis* and *M. leprae*. High mycolic acid content in cell wall resists alcohol-acid decolorization (20% H2SO4 for *M. tb*, 5% for *M. leprae*). Organisms appear bright red/magenta against methylene blue background.

## 2. Common Culture Media in Clinical Laboratory
- **Blood Agar (Enriched + Differential)**: Contains 5% sheep blood. Differentiates hemolytic patterns:
  - *Beta-hemolysis:* Complete lysis with clear halo (*Streptococcus pyogenes*, *Staph aureus*).
  - *Alpha-hemolysis:* Partial lysis with greenish discoloration (*Streptococcus pneumoniae*, *Viridans streptococci*).
  - *Gamma-hemolysis:* No hemolysis (*Enterococcus faecalis*).
- **MacConkey Agar (Selective + Differential)**: Contains bile salts and crystal violet (inhibits Gram-positives) plus lactose and neutral red indicator.
  - *Lactose Fermenters (Pink colonies):* *Escherichia coli*, *Klebsiella pneumoniae*.
  - *Non-Lactose Fermenters (Pale/Colorless colonies):* *Salmonella*, *Shigella*, *Pseudomonas aeruginosa*.

## 3. Antimicrobial Susceptibility Testing (AST)
- **Kirby-Bauer Disk Diffusion**: Performed on Mueller-Hinton Agar (MHA) standardized at 4 mm depth and pH 7.2–7.4, inoculated with 0.5 McFarland bacterial suspension.
- **Zone of Inhibition**: Measured in millimeters and compared against Clinical and Laboratory Standards Institute (CLSI) breakpoint tables to report Susceptible (S), Intermediate (I), or Resistant (R).
""",
        },
        {
            "title": "Hematology Pearls: Anemia Classification & Peripheral Smear Diagnosis",
            "subject": "Pathology",
            "topic": "Hematology & Blood Disorders",
            "course": "MBBS",
            "curriculum": "Pondicherry University",
            "academic_year": "Year 2",
            "material_type": "notes",
            "difficulty_level": "medium",
            "summary": "Microcytic, normocytic, and macrocytic anemia algorithms; peripheral blood smear findings for Iron Deficiency, Megaloblastic, and Sickle Cell anemia.",
            "content": """# Hematology: Diagnostic Approach to Anemias

## 1. Morphological Classification by Mean Corpuscular Volume (MCV)
- **Microcytic Hypochromic Anemia (MCV < 80 fL)**:
  - *Differential Diagnosis:* Iron Deficiency Anemia (IDA), Thalassemia Trait, Anemia of Chronic Disease (ACD), Sideroblastic Anemia, Lead Poisoning.
  - *Mentzer Index (MCV / RBC count):* < 13 suggests Thalassemia trait; > 13 suggests Iron Deficiency Anemia.
  - *Iron Studies:*
    - **IDA:** Serum Ferritin ↓, Serum Iron ↓, Total Iron Binding Capacity (TIBC) ↑, Transferrin Saturation < 15%.
    - **ACD:** Serum Ferritin ↑ (acute phase reactant), Serum Iron ↓, TIBC ↓.
    - **Thalassemia:** Serum Ferritin Normal or ↑, Serum Iron Normal.
- **Macrocytic Anemia (MCV > 100 fL)**:
  - *Megaloblastic (Impaired DNA synthesis):* Vitamin B12 deficiency (neurological signs + methylmalonic acid ↑) or Folate deficiency (serum homocysteine ↑, normal methylmalonic acid). Peripheral smear shows hypersegmented neutrophils (≥ 5 lobes in > 5% of PMNs).
  - *Non-Megaloblastic:* Alcoholism, liver disease, hypothyroidism, myelodysplastic syndrome (MDS).
- **Normocytic Normochromic Anemia (MCV 80–100 fL)**:
  - High Reticulocyte Count (> 2–3%): Hemolysis (immune hemolytic anemia, G6PD deficiency, hereditary spherocytosis) or Acute hemorrhage.
  - Low Reticulocyte Count (< 2%): Aplastic anemia, bone marrow infiltration (leukemia), chronic renal failure (low erythropoietin).

## 2. Characteristic Peripheral Smear Clues
- **Target Cells (Codocytes)**: Thalassemia, Hemoglobin C disease, post-splenectomy, chronic liver disease.
- **Schistocytes (Helmet Cells)**: Microangiopathic Hemolytic Anemia (TTP, HUS, DIC) or mechanical prosthetic heart valves.
- **Bite Cells and Heinz Bodies**: G6PD deficiency with oxidative hemolysis (dapsone, primaquine, fava beans).
- **Sickle Cells (Drepanocytes)**: Hemoglobin SS disease (glutamic acid to valine substitution at position 6 of beta-globin chain).
""",
        },
        {
            "title": "Systemic Virology & National Immunization Protocol",
            "subject": "Microbiology",
            "topic": "Virology & Immunization",
            "course": "MBBS",
            "curriculum": "Pondicherry University",
            "academic_year": "Year 2",
            "material_type": "important_questions",
            "difficulty_level": "medium",
            "summary": "Hepatitis B serology interpretation; Dengue diagnostic markers (NS1 vs IgM/IgG); rabies post-exposure prophylaxis; Universal Immunization Programme (UIP).",
            "content": """# Systemic Virology & Public Health Immunization

## 1. Hepatitis B Serological Markers & Clinical Interpretation
| Clinical Status | HBsAg | Anti-HBs | Anti-HBc IgM | Anti-HBc IgG | HBeAg |
|---|---|---|---|---|---|
| Acute Hepatitis B | **Positive** | Negative | **Positive** | Negative | Positive |
| Window Period | Negative | Negative | **Positive** | Variable | Negative |
| Chronic Infection (Active) | **Positive** | Negative | Negative | **Positive** | **Positive** |
| Recovery / Natural Immunity | Negative | **Positive** | Negative | **Positive** | Negative |
| Vaccinated Immunity | Negative | **Positive** | Negative | Negative | Negative |

## 2. Dengue Virus Diagnostics
- **Day 1 to Day 5 (Acute Viraemic Phase)**: Detect **Dengue NS1 Antigen** via ELISA or rapid immunochromatography (sensitivity > 90% in first 48 hours). RT-PCR detects viral RNA serotypes (DEN-1 to DEN-4).
- **Day 5 onwards (Convalescent Phase)**: Detect **Anti-Dengue IgM Antibodies**. IgM peaks around day 10–14 and persists for 2–3 months.
- **Warning Signs of Severe Dengue**: Persistent vomiting, severe abdominal pain, clinical fluid accumulation (ascites, pleural effusion), mucosal bleed, lethargy/restlessness, hepatomegaly > 2 cm, rapid drop in platelet count concurrent with hematocrit rise.

## 3. India's Universal Immunization Programme (UIP) Timetable
- **At Birth**: BCG (intradermal, left upper arm), OPV zero dose (oral), Hepatitis B birth dose (intramuscular, anterolateral thigh within 24 hrs).
- **6, 10, 14 Weeks**: Pentavalent vaccine (DPT + Hep B + Hib), Oral Polio Vaccine (OPV 1, 2, 3), Inactivated Polio Vaccine (fIPV fractional intradermal), Rotavirus, Pneumococcal Conjugate Vaccine (PCV 1 and 2 at 6 & 14 weeks).
- **9–12 Months**: MR (Measles-Rubella 1st dose), Japanese Encephalitis (JE 1st dose in endemic districts), PCV Booster, Vitamin A (1 lakh IU).
- **16–24 Months**: MR 2nd dose, DPT Booster 1, OPV Booster, JE 2nd dose, Vitamin A (2 lakh IU every 6 months up to 5 years).
""",
        },
        {
            "title": "Forensic Thanatology, Toxicology & Medical Jurisprudence",
            "subject": "Forensic Medicine",
            "topic": "Thanatology, Poisons & Medical Law",
            "course": "MBBS",
            "curriculum": "Pondicherry University",
            "academic_year": "Year 2",
            "material_type": "notes",
            "difficulty_level": "medium",
            "summary": "Post-mortem interval markers (rigor mortis, livor mortis, algor mortis); organophosphate poisoning management and atropine protocol; informed consent laws.",
            "content": """# Forensic Medicine: Thanatology & Emergency Toxicology

## 1. Post-Mortem Interval (PMI) Estimation
- **Algor Mortis (Cooling of the Body)**: Most reliable in the first 12–18 hours. Normal body cools at approximately 0.5–0.7 °C per hour under moderate climatic conditions (Henssge's nomogram).
- **Livor Mortis (Post-Mortem Lividity / Hypostasis)**:
  - Appears: 1–2 hours after death.
  - Fully formed / Fixed: 6–8 hours after death (blanching stops on thumb pressure).
  - *Color indicators:* Cherry red (Carbon Monoxide poisoning), Chocolate brown (Methemoglobinemia / Potassium chlorate), Pinkish-red (Cyanide poisoning or hypothermia).
- **Rigor Mortis**:
  - Commences in involuntary muscles of heart and diaphragm within 1–2 hours.
  - Progresses in voluntary muscles in cranio-caudal direction (Nysten's Law: eyelids → jaw → neck → upper limbs → trunk → lower limbs).
  - *Timeline in temperate climates:* Appears in 12 hours, persists for 12 hours, disappears in 12 hours ('Rule of 12s'). Accelerated in high ambient temperature and pre-mortem convulsions.

## 2. Toxicology: Organophosphate Poisoning Protocol
- **Mechanism**: Irreversible inhibition of Acetylcholinesterase (AChE), causing massive acetylcholine accumulation at muscarinic and nicotinic receptors.
- **SLUDGE-BBB Signs**: Salivation, Lacrimation, Urination, Defecation, Gastric upset, Emesis, Bronchoconstriction, Bronchorrhea, Bradycardia.
- **Emergency Management**:
  1. Decontamination: Remove clothing, wash skin thoroughly with soap and water.
  2. Airway support & high-flow oxygen.
  3. **Atropine**: Competitive antagonist at muscarinic receptors. Initial dose 1.8–3.0 mg IV bolus; double dose every 3–5 minutes until full atropinization achieved (**clear chest on auscultation**, heart rate > 80 bpm, systolic BP > 80 mmHg, dry axillae, dilated pupils).
  4. **Pralidoxime (2-PAM)**: Cholinesterase reactivator. 1–2 g IV infusion over 30 min, effective if given before enzyme aging occurs (< 24–48 hours).

## 3. Medical Law & Ethics: Informed Consent
- **Voluntary & Informed**: The patient must have decision-making capacity, receive all material information (diagnosis, proposed procedure, alternatives, potential risks, and consequences of refusal), and grant consent free of coercion.
- **Emergency Exception (Doctrine of Necessity)**: Life-saving interventions do not require prior consent if the patient is unconscious or incapacitated and no legal surrogate is immediately available.
""",
        },
        {
            "title": "Clinical Examination & Bedside Auscultation Manual",
            "subject": "General Medicine",
            "topic": "Clinical Skills & Physical Examination",
            "course": "MBBS",
            "curriculum": "Pondicherry University",
            "academic_year": "Year 2",
            "material_type": "learning_material",
            "difficulty_level": "difficult",
            "summary": "Cardiovascular exam: heart sounds, systolic vs diastolic murmurs; respiratory crackles vs wheezes; JVP waveform analysis and abdomen quadrant palpation.",
            "content": """# Bedside Clinical Examination & Diagnostic Skills

## 1. Cardiovascular System: Auscultation & Murmurs
- **Heart Sounds**:
  - **S1**: Closure of Mitral and Tricuspid valves. Loudest at the cardiac apex. Marks the beginning of ventricular systole.
  - **S2**: Closure of Aortic (A2) and Pulmonary (P2) valves. Loudest at the base (2nd right and left intercostal spaces). Physiological splitting occurs during inspiration.
  - **S3 (Ventricular Gallop)**: Rapid ventricular filling into a dilated ventricle. Pathological in adults over 40 (sign of systolic heart failure or severe mitral regurgitation).
  - **S4 (Atrial Gallop)**: Atrial contraction against a stiff, hypertrophied ventricle (systemic hypertension, aortic stenosis, hypertrophic cardiomyopathy).
- **Murmur Characterization**:
  - **Aortic Stenosis**: Harsh crescendo-decrescendo systolic murmur at 2nd right intercostal space radiating to the carotids. Associated with slow-rising pulse (*pulsus parvus et tardus*).
  - **Mitral Regurgitation**: Holosystolic / pansystolic blowing murmur at apex radiating to the left axilla. Loudest in left lateral decubitus.
  - **Mitral Stenosis**: Low-pitched rumbling mid-diastolic murmur preceded by an **Opening Snap** at the apex with the bell of the stethoscope in left lateral position.
  - **Aortic Regurgitation**: High-pitched early diastolic decrescendo blowing murmur at left sternal edge (Erb's point) with patient sitting forward in full expiration.

## 2. Jugular Venous Pressure (JVP) Waveform Analysis
- **'a' wave**: Atrial contraction (absent in Atrial Fibrillation; prominent 'cannon a waves' in Complete Heart Block).
- **'c' wave**: Bulging of tricuspid valve during early ventricular isovolumetric contraction.
- **'x' descent**: Atrial relaxation and downward displacement of tricuspid valve during ventricular systole.
- **'v' wave**: Venous filling of the right atrium against closed tricuspid valve during late systole.
- **'y' descent**: Rapid emptying of right atrium into right ventricle upon tricuspid valve opening (steep 'y' descent in Constrictive Pericarditis; attenuated in Cardiac Tamponade).

## 3. Respiratory System: Breath Sounds & Added Sounds
- **Vesicular Breath Sounds**: Soft, rustling sound heard over peripheral lung fields; inspiratory phase longer than expiratory phase (3:1) with no pause.
- **Bronchial Breath Sounds**: Hollow, tubular sound with equal inspiratory and expiratory duration and a clear pause between phases. Normal over trachea; indicates **lung consolidation** (pneumonia) over peripheral lobes.
- **Crackles (Rales)**: Non-musical, discontinuous sounds caused by sudden explosive opening of small airways. Fine crackles: Pulmonary fibrosis, early pulmonary edema. Coarse crackles: Bronchiectasis, severe pneumonia.
- **Wheezes (Rhonchi)**: Continuous musical high-pitched sounds caused by airway narrowing and airflow limitation (Bronchial Asthma, COPD).
""",
        },
    ]


def ensure_mbbs_materials(db: Session) -> None:
    """Ensure MBBS study materials exist in the database."""
    try:
        # Find or create a teacher uploader
        teacher = db.query(Student).filter(Student.role == "teacher").first()
        uploader_id = teacher.id if teacher else None

        for item in get_mbbs_materials_data():
            existing = db.query(StudyMaterial).filter(
                StudyMaterial.title == item["title"]
            ).first()
            if not existing:
                mat = StudyMaterial(
                    title=item["title"],
                    subject=item["subject"],
                    topic=item["topic"],
                    course=item["course"],
                    curriculum=item["curriculum"],
                    academic_year=item["academic_year"],
                    material_type=item["material_type"],
                    difficulty_level=item["difficulty_level"],
                    summary=item["summary"],
                    content=item["content"],
                    uploaded_by=uploader_id,
                )
                db.add(mat)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Warning in ensure_mbbs_materials: {e}")
