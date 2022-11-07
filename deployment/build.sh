#!/bin/sh

# myfolio_packages 폴더가 존재하면 삭제
if [ -d "myfolio_packages" ]; then
  rm -r myfolio_packages*
fi

# myfolio_packages 폴더 생성
mkdir myfolio_packages

# 활성화된 가상 환경을 package 폴더에 복사
cp -r "$VIRTUAL_ENV"/lib/python3.9/site-packages/* package

# 제거해야 하는 라이브러리를 myfolio_packages 폴더에서 제거
rm -r myfolio_packages/psycopg2
rm -r myfolio_packages/psycopg2_*
rm -r myfolio_packages/boto3*
rm -r myfolio_packages/pip*

# myfolio_packages 폴더를 myfolio_packages.zip으로 압축 후 삭제
cd myfolio_packages
zip -r ../myfolio_packages.zip .
cd ..
rm -r myfolio_packages
