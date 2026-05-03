import os
from openai import OpenAI
from tools.policy_search import search_policy_docs

SYSTEM_PROMPT = '''You are an HR Case Resolution Agent. Answer based only on the provided HR policy context and employee profile. Be clear, professional, and concise. If policy context is missing, say it needs HR review. Never invent company policy.'''

def _fallback_answer(category, message, employee, policy_results):
    if category == 'leave':
        return f"Your current leave balance is {employee.leave_balance} days. Based on company policy, annual leave requests should be submitted at least 3 working days in advance."
    if policy_results:
        top = policy_results[0]
        return f"Based on {top['source']}: {top['text'][:700]}"
    return 'I could not find a matching HR policy. I created a ticket so HR can review this case.'

def resolve_case(category: str, message: str, employee):
    policy_results = search_policy_docs(message + ' ' + category)
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        try:
            context = '\n\n'.join([f"SOURCE: {r['source']}\n{r['text']}" for r in policy_results]) or 'No matching policy found.'
            client = OpenAI(api_key=api_key)
            res = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user', 'content': f"Employee: {employee.name}, dept: {employee.department}, leave balance: {employee.leave_balance}\nCategory: {category}\nQuestion: {message}\nPolicy context:\n{context}"}
                ],
                temperature=0.2,
            )
            return res.choices[0].message.content.strip(), bool(policy_results)
        except Exception as e:
            return _fallback_answer(category, message, employee, policy_results), bool(policy_results)
    return _fallback_answer(category, message, employee, policy_results), bool(policy_results)
