import sys
import re
from collections import Counter
from kiwipiepy import Kiwi

def process_file(file_path):
    try:
        # 파일 열기
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # 형태소 분석기 초기화 (Kiwi)
        kiwi = Kiwi()
        
        # 1. 어절(띄어쓰기 덩어리) 단위로 먼저 분리
        words = text.split()
        
        meaningful_words = []
        
        for w in words:
            # 특수 기호 제거 (단어의 양 끝부분만 제거하여 형태 유지)
            w_clean = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', w)
            if not w_clean:
                continue

            # 2. 형태소 분석 (단어 안에서 조사만 분리해내기 위함)
            tokens = kiwi.tokenize(w_clean)
            if not tokens:
                continue
            
            # 뒤에서부터 분석하여, 조사(Josa, 품사 태그가 'J'로 시작)인 부분만 잘라냅니다.
            cut_idx = len(w_clean)
            for token in reversed(tokens):
                if token.tag.startswith('J'):
                    cut_idx = token.start
                else:
                    break # 조사가 아닌 성분이 나오면 자르기 중단
            
            # 조사를 떼어낸 핵심 단어 (예: '스파이더가' -> '스파이더', '맹렬하게' -> '맹렬하게')
            core_word = w_clean[:cut_idx]
            
            # 1글자 단어 제외 및 유의미한 단어만 수집
            if len(core_word) > 1:
                meaningful_words.append(core_word)

        # 3. 빈도수 계산
        word_counts = Counter(meaningful_words)

        # 4. 상위 결과 출력
        top_words = word_counts.most_common(100)
        
        if not top_words:
            print("추출된 유의미한 단어가 없습니다.")
            return

        print(f"--- '{file_path}' 단어 빈도수 분석 결과 (상위 100개, 명사/동사/형용사 위주) ---")
        for rank, (word, count) in enumerate(top_words, start=1):
            print(f"{rank}, {word}, {count}번")

    except FileNotFoundError:
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python word_counter.py 문서명.md")
        sys.exit(1)
    
    target_file = sys.argv[1]
    process_file(target_file)
