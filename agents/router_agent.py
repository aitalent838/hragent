def classify_case(message: str) -> str:
    m = message.lower()
    if any(w in m for w in ['leave', 'annual', 'vacation', 'mc', 'sick']):
        return 'leave'
    if any(w in m for w in ['claim', 'medical', 'dental', 'hospital', 'clinic', 'surgery']):
        return 'medical_claim'
    if any(w in m for w in ['salary', 'payroll', 'payslip', 'bonus', 'deduction', 'overtime']):
        return 'payroll'
    if any(w in m for w in ['join', 'onboard', 'new staff', 'orientation', 'probation']):
        return 'onboarding'
    if any(w in m for w in ['complaint', 'unfair', 'harass', 'disciplinary', 'warning']):
        return 'employee_relations'
    return 'general_policy'

def priority_for(message: str, category: str) -> str:
    urgent_terms = ['urgent', 'immediately', 'today', 'emergency', 'harass', 'unsafe']
    if any(t in message.lower() for t in urgent_terms):
        return 'high'
    if category in ['employee_relations', 'payroll']:
        return 'high'
    return 'medium'
