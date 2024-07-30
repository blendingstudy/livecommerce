class IamportPayment {
    constructor(merchantId) {
        this.IMP = window.IMP;
        this.IMP.init(merchantId);
    }

    async requestPay(paymentData) {
        return new Promise((resolve, reject) => {
            this.IMP.request_pay(paymentData, (response) => {
                if (response.success) {
                    resolve(response);
                } else {
                    reject(new Error(response.error_msg));
                }
            });
        });
    }

    async verifyPayment(orderId, impUid, merchantUid) {
        console.log('Sending verification request:', { orderId, impUid, merchantUid });
        try {
            const response = await fetch(`/verify/${orderId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    imp_uid: impUid,
                    merchant_uid: merchantUid
                })
            });
    
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Payment verification failed: ${errorData.message || response.statusText}`);
            }
    
            return await response.json();
        } catch (error) {
            console.error('Payment verification error:', error);
            throw error;
        }
    }

    getCsrfToken() {
        console.log('hi');
        const token = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        if (!token) {
            console.error('CSRF token not found');
        }
        return token;
    }
}

const iamportPayment = new IamportPayment('imp38825147');

document.addEventListener('DOMContentLoaded', () => {
    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const orderData = {
                orderId: paymentForm.dataset.orderId,
                productName: paymentForm.dataset.productName,
                totalPrice: parseFloat(document.getElementById('final-price').textContent.replace(/[^0-9.-]+/g,"")),
                buyerEmail: document.getElementById('buyer-email').value,
                buyerName: document.getElementById('buyer-name').value,
                buyerTel: document.getElementById('buyer-tel').value,
            };
            
            try {
                const paymentData = {
                    pg: "html5_inicis",
                    pay_method: "card",
                    merchant_uid: `order_${orderData.orderId}`,
                    name: orderData.productName,
                    amount: Math.round(orderData.totalPrice), // 소수점 제거 및 반올림
                    buyer_email: orderData.buyerEmail,
                    buyer_name: orderData.buyerName,
                    buyer_tel: orderData.buyerTel,
                };
                
                const response = await iamportPayment.requestPay(paymentData);
                const verificationResult = await iamportPayment.verifyPayment(
                    orderData.orderId,
                    response.imp_uid,
                    response.merchant_uid
                );

                if (verificationResult.success) {
                    alert('결제가 성공적으로 완료되었습니다.');
                    window.location.href = `/order_status/${orderData.orderId}`;
                } else {
                    alert('결제 검증에 실패했습니다: ' + verificationResult.message);
                }
            } catch (error) {
                console.error('Payment error:', error);
                alert('결제 중 오류가 발생했습니다: ' + error.message);
            }
        });
    }
});