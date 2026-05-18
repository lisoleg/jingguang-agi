from task_interface import TextProcessor
p = TextProcessor()
text = '这个系统非常excellent和amazing！'
text_lower = text.lower()
print('text_lower:', text_lower)
print('excellent in text_lower?', 'excellent' in text_lower)
print('amazing in text_lower?', 'amazing' in text_lower)
result = p.understand(text)
print('result sentiment:', result['sentiment'])
print('rule sentiment:', p._rule_based_sentiment(text_lower))
