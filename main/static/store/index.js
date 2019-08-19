import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex);
const state={
    status:"",
    login_user:""

};
const getters = {
    isShow(state) {  //方法名随意,主要是来承载变化的showFooter的值
       return state.status
    },
    getLoginUser(){  //方法名随意,主要是用来承载变化的changableNum的值
       return state.login_user
    }
};
const mutations = {
    show(state) {   //自定义改变state初始值的方法，这里面的参数除了state之外还可以再传额外的参数(变量或对象);
        state.status = true;
    },
    hide(state) {  //同上
        state.login_user = false;
    },

};

const actions = {
    hideFooter(context) {  //自定义触发mutations里函数的方法，context与store 实例具有相同方法和属性
        context.commit('show');
    },
    showFooter(context) {  //同上注释
        context.commit('hide');
    },
};

const store = new Vuex.Store({
    state,
    getters,
    mutations,actions
});

export default store;