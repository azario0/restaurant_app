new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        cartItems: []
    },
    computed: {
        cartTotal() {
            return this.cartItems.reduce((total, item) => total + item.price * item.quantity, 0);
        }
    },
    methods: {
        addToCart(id, name, price) {
            const existingItem = this.cartItems.find(item => item.id === id);
            if (existingItem) {
                existingItem.quantity++;
            } else {
                this.cartItems.push({ id, name, price, quantity: 1 });
            }
            this.saveCart();
        },
        removeFromCart(id) {
            const index = this.cartItems.findIndex(item => item.id === id);
            if (index !== -1) {
                this.cartItems.splice(index, 1);
                this.saveCart();
            }
        },
        saveCart() {
            localStorage.setItem('cart', JSON.stringify(this.cartItems));
        },
        loadCart() {
            const cart = localStorage.getItem('cart');
            if (cart) {
                this.cartItems = JSON.parse(cart);
            }
        },
        submitOrder() {
            // The form will be submitted normally, and the cart will be sent as a hidden input
            localStorage.removeItem('cart');
        }
    },
    mounted() {
        this.loadCart();
    }
});