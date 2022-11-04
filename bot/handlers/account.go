package handlers

import (
	"invest_blango_criptal_backend/models"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

type newUserPassword struct {
	NewPassword string `json:"user_id" binding:"required"`
}


func (h *Handler) changePasssord(c *gin.Context) {
	var input newUserPassword


	if err := c.BindJSON(&input); err != nil {
		newErrorResponse(c, http.StatusBadRequest, "Invalid json parameters")
		return
	}

	userId, _ := c.Get(userCtx)
	userPassword, _ := c.Get(passwordCtx)

	id, err := h.services.ChangePassword(userId.(int64), userPassword.(string))
	if err != nil {
		logrus.Error(err)
		newErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	c.JSON(http.StatusCreated, map[string]interface{}{
		"id": id,
	})
}


func (h *Handler) getAccountData(c *gin.Context) {
	userLogin := c.Query("login")
	userPassword := c.Query("user_password")

	user, err := h.services.GetUser(models.SingIn{Login: userLogin, Password: userPassword})
	if err != nil {
		logrus.Error(err)
		newErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	c.JSON(http.StatusCreated, map[string]interface{}{
		"data": user,		
	})		
}


func (h *Handler) updateAccountDocs(c *gin.Context) {
	var docs models.UserDocs

	if err := c.BindJSON(&docs); err != nil {
		logrus.Error(err)
		newErrorResponse(c, http.StatusBadRequest, "Invalid json parameters")
		return
	}

	userId, _ := c.Get(userCtx)
	
	id, err := h.services.EditUserData(userId.(int64), docs)

	if err != nil {
		logrus.Error(err)
		newErrorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	c.JSON(http.StatusOK, map[string]interface{}{
		"id": id,		
	})		
}