package handlers

import (
	"fmt"
	"invest_blango_criptal_backend/models"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

func (h *Handler) singUp(c *gin.Context) {
	var input models.User
	
	fmt.Println(input)
	if err := c.BindJSON(&input); err != nil {
		newErrorResponse(c, http.StatusBadRequest, "Invalid json parameters")
		return
	}
	

	id, err := h.services.CreateUser(input)
	if err != nil {
		logrus.Error(err)
		newErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	c.JSON(http.StatusCreated, map[string]interface{}{
		"id": id,
	})
}

func (h *Handler) singIn(c *gin.Context) {
	var input models.SingIn

	if err := c.BindJSON(&input); err != nil {
		logrus.Error(err)
		newErrorResponse(c, http.StatusBadRequest, "Invalid json parameters")
		return
	}
	
	_, err := h.services.Authorization.GetUser(input)
	if err != nil {
		newErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	token, err := h.services.GenerateJWTToken(input)
	if err != nil {
		logrus.Error(err)
		newErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}
	
	c.JSON(http.StatusCreated, map[string]interface{}{
		"access_token": token,
	})
}