import spacy
from IPython.core.display import display, HTML

nlp_ner = spacy.load("model-best")

doc = nlp_ner("Antiretroviral therapy (ART) is recommended for all HIV-infected\
individuals to reduce the risk of disease progression.\nART also is recommended \
for HIV-infected individuals for the prevention of transmission of HIV.\nPatients \
starting ART should be willing and able to commit to treatment and understand the\
benefits and risks of therapy and the importance of adherence. Patients may choose\
to postpone therapy, and providers, on a case-by-case basis, may elect to defer\
therapy on the basis of clinical and/or psychosocial factors.")

colors = {"PATHOGEN": "#F67DE3", "MEDICINE": "#7DF6D9", "MEDICALCONDITION":"#FFFFFF"}
options = {"colors": colors} 

#html = spacy.displacy.render(doc, style="ent", options= options, page=True)
spacy.displacy.serve(doc, style="ent", options= options)
#http://localhost:5000/
#display(HTML(html))